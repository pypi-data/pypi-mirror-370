# Modifications Copyright(C)[2025] Advanced Micro Devices, Inc. All rights reserved.
# https://github.com/thunlp/TritonBench - Apache License 2.0
import torch

import triton
import triton.language as tl
import math
import torch.nn.functional as F

TESLA = "Tesla" in torch.cuda.get_device_name(0)

@triton.jit
def _fwd_kernel(
    Q,
    K,
    V,
    sm_scale,
    B_Start_Loc,
    B_Seqlen,  # B_LOC 内部记录每个batch 输入的真实位置， B_SEQ_len 记录当前输入的真实长度
    Out,
    Req_to_tokens,
    B_req_idx,
    stride_qbs,
    stride_qh,
    stride_qd,
    stride_kbs,
    stride_kh,
    stride_kd,
    stride_vbs,
    stride_vh,
    stride_vd,
    stride_obs,
    stride_oh,
    stride_od,
    stride_req_to_tokens_b,
    stride_req_to_tokens_s,
    kv_group_num,
    b_prompt_cache_len,
    head_dim: tl.constexpr,
    BLOCK_M: tl.constexpr,
    BLOCK_DMODEL: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    cur_batch = tl.program_id(0)
    cur_head = tl.program_id(1)
    start_m = tl.program_id(2)

    cur_kv_head = cur_head // kv_group_num

    cur_batch_in_all_start_index = tl.load(B_Start_Loc + cur_batch)
    prompt_cache_len = tl.load(b_prompt_cache_len + cur_batch)
    cur_batch_seq_len = tl.load(B_Seqlen + cur_batch) - prompt_cache_len
    cur_batch_req_idx = tl.load(B_req_idx + cur_batch)

    block_start_loc = BLOCK_M * start_m

    # initialize offsets
    offs_n = tl.arange(0, BLOCK_N)
    offs_d = tl.arange(0, BLOCK_DMODEL)
    offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    off_q = (
        (cur_batch_in_all_start_index + offs_m[:, None]) * stride_qbs
        + cur_head * stride_qh
        + offs_d[None, :] * stride_qd
    )

    q = tl.load(Q + off_q, mask=(offs_m[:, None] < cur_batch_seq_len) & (offs_d[None, :] < head_dim), other=0.0)

    # initialize pointer to m and l
    m_i = tl.zeros([BLOCK_M], dtype=tl.float32) - float("inf")
    l_i = tl.zeros([BLOCK_M], dtype=tl.float32)
    acc = tl.zeros([BLOCK_M, BLOCK_DMODEL], dtype=tl.float32)

    block_mask = tl.where(block_start_loc < cur_batch_seq_len, 1, 0)
    block_end_loc = tl.minimum((start_m + 1) * BLOCK_M + prompt_cache_len, cur_batch_seq_len + prompt_cache_len)

    for start_n in range(0, block_mask * block_end_loc, BLOCK_N):
        start_n = tl.multiple_of(start_n, BLOCK_N)
        # -- compute qk ----
        kv_loc = tl.load(
            Req_to_tokens + stride_req_to_tokens_b * cur_batch_req_idx + stride_req_to_tokens_s * (start_n + offs_n),
            mask=(start_n + offs_n) < block_end_loc,
            other=0,
        )
        off_k = kv_loc[None, :] * stride_kbs + cur_kv_head * stride_kh + offs_d[:, None] * stride_kd
        k = tl.load(
            K + off_k, mask=((start_n + offs_n[None, :]) < block_end_loc) & (offs_d[:, None] < head_dim), other=0.0
        )

        qk = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)
        qk += tl.dot(q, k)
        qk *= sm_scale
        qk = tl.where(offs_m[:, None] + prompt_cache_len >= start_n + offs_n[None, :], qk, float("-100000000.0"))

        # -- compute m_ij, p, l_ij
        m_ij = tl.max(qk, 1)
        p = tl.exp(qk - m_ij[:, None])
        l_ij = tl.sum(p, 1)
        # -- update m_i and l_i
        m_i_new = tl.maximum(m_i, m_ij)
        alpha = tl.exp(m_i - m_i_new)
        beta = tl.exp(m_ij - m_i_new)
        l_i_new = alpha * l_i + beta * l_ij
        # -- update output accumulator --
        # scale p
        p_scale = beta / l_i_new
        p = p * p_scale[:, None]
        # scale acc
        acc_scale = l_i / l_i_new * alpha
        acc_scale = tl.where(offs_m + prompt_cache_len >= start_n, acc_scale, 1.0)
        acc = acc * acc_scale[:, None]
        # update acc
        off_v = kv_loc[:, None] * stride_vbs + cur_kv_head * stride_vh + offs_d[None, :] * stride_vd
        v = tl.load(
            V + off_v, mask=((start_n + offs_n[:, None]) < block_end_loc) & (offs_d[None, :] < head_dim), other=0.0
        )
        p = p.to(v.dtype)
        acc += tl.dot(p, v)
        # update m_i and l_i
        l_i = l_i_new
        m_i = m_i_new
    # initialize pointers to output
    off_o = (
        (cur_batch_in_all_start_index + offs_m[:, None]) * stride_obs
        + cur_head * stride_oh
        + offs_d[None, :] * stride_od
    )
    out_ptrs = Out + off_o
    tl.store(out_ptrs, acc, mask=(offs_m[:, None] < cur_batch_seq_len) & (offs_d[None, :] < head_dim))
    return


@torch.no_grad()
def context_attention_fwd(
    q, k, v, o, b_req_idx, b_start_loc, b_seq_len, b_prompt_cache_len, max_input_len, req_to_token_indexs
):
    BLOCK = 128 if not TESLA else 64
    # shape constraints
    Lq, Lk, Lv = q.shape[-1], k.shape[-1], v.shape[-1]
    assert Lq == Lk and Lk == Lv
    head_dim = Lq
    BLOCK_DMODEL = triton.next_power_of_2(head_dim)

    sm_scale = 1.0 / (Lq ** 0.5)  # 计算scale系数
    batch, head = b_seq_len.shape[0], q.shape[1]
    kv_group_num = q.shape[1] // k.shape[1]

    grid = (batch, head, triton.cdiv(max_input_len, BLOCK))  # batch, head,

    num_warps = 4 if Lk <= 64 else 8
    _fwd_kernel[grid](
        q,
        k,
        v,
        sm_scale,
        b_start_loc,
        b_seq_len,
        o,
        req_to_token_indexs,
        b_req_idx,
        q.stride(0),
        q.stride(1),
        q.stride(2),
        k.stride(0),
        k.stride(1),
        k.stride(2),
        v.stride(0),
        v.stride(1),
        v.stride(2),
        o.stride(0),
        o.stride(1),
        o.stride(2),
        req_to_token_indexs.stride(0),
        req_to_token_indexs.stride(1),
        kv_group_num=kv_group_num,
        b_prompt_cache_len=b_prompt_cache_len,
        head_dim=head_dim,
        BLOCK_M=BLOCK,
        BLOCK_DMODEL=BLOCK_DMODEL,
        BLOCK_N=BLOCK,
        num_warps=num_warps,
        num_stages=1,
    )
    return o




##################################################################################################################################################


import torch
import numpy as np

def test_context_attention_fwd():
    Z, H, N_CTX, D_HEAD = 10, 6, 500, 96
    dtype = torch.float16
    Z = 1
    q = torch.empty((Z * N_CTX, H, D_HEAD), dtype=dtype, device="cuda").normal_(mean=0.1, std=0.2)
    k = torch.empty((Z * N_CTX + 7000, H, D_HEAD), dtype=dtype, device="cuda").normal_(mean=0.4, std=0.2)
    v = torch.empty((Z * N_CTX + 7000, H, D_HEAD), dtype=dtype, device="cuda").normal_(mean=0.3, std=0.2)
    o = torch.empty((Z * N_CTX, H, D_HEAD), dtype=dtype, device="cuda").normal_(mean=0.3, std=0.2)
    req_to_token_indexs = torch.zeros((10, Z * N_CTX + 7000), dtype=torch.int32, device="cuda")
    max_input_len = N_CTX
    Z = 1
    b_start_loc = torch.zeros((Z,), dtype=torch.int32, device="cuda")
    b_seq_len = torch.ones((Z,), dtype=torch.int32, device="cuda")
    b_req_idx = torch.ones((Z,), dtype=torch.int32, device="cuda")
    b_prompt_cache_len = torch.zeros(1, dtype=torch.int32, device="cuda")
    b_prompt_cache_len[0] = 0
    prompt_cache_len = 0

    b_seq_len[0] = 500
    b_req_idx[0] = 0
    req_to_token_indexs[0][: prompt_cache_len + N_CTX] = torch.tensor(
        np.arange(prompt_cache_len + N_CTX), dtype=torch.int32
    ).cuda()

    result_gold = context_attention_fwd(
        q,
        k,
        v,
        o,
        b_req_idx,
        b_start_loc,
        b_seq_len + prompt_cache_len,
        b_prompt_cache_len,
        max_input_len,
        req_to_token_indexs,
    )
    return result_gold

result_gold = test_context_attention_fwd()

# Modifications Copyright(C)[2025] Advanced Micro Devices, Inc. All rights reserved.
# https://github.com/thunlp/TritonBench - Apache License 2.0
import torch
import triton
import triton.language as tl

@triton.jit
def _fwd_kernel_flash_decode_stage2(
    B_Seqlen,
    Mid_O,  # [batch, head, seq_block_num, head_dim]
    Mid_O_LogExpSum,  # [batch, head, seq_block_num]
    Out,  # [batch, head, head_dim]
    stride_mid_ob,
    stride_mid_oh,
    stride_mid_os,
    stride_mid_od,
    stride_mid_o_eb,
    stride_mid_o_eh,
    stride_mid_o_es,
    stride_obs,
    stride_oh,
    stride_od,
    head_dim,
    BLOCK_SEQ: tl.constexpr,
    BLOCK_DMODEL: tl.constexpr,
):
    cur_batch = tl.program_id(0)
    cur_head = tl.program_id(1)

    offs_d = tl.arange(0, BLOCK_DMODEL)
    cur_batch_seq_len = tl.load(B_Seqlen + cur_batch)

    block_n_size = tl.where(cur_batch_seq_len <= 0, 0, cur_batch_seq_len + BLOCK_SEQ - 1) // BLOCK_SEQ

    sum_exp = 0.0
    max_logic = -float("inf")
    acc = tl.zeros([BLOCK_DMODEL], dtype=tl.float32)

    offs_v = cur_batch * stride_mid_ob + cur_head * stride_mid_oh + offs_d
    offs_logic = cur_batch * stride_mid_o_eb + cur_head * stride_mid_o_eh
    for block_seq_n in range(0, block_n_size, 1):
        tv = tl.load(Mid_O + offs_v + block_seq_n * stride_mid_os, mask=offs_d < head_dim, other=0.0)
        tlogic = tl.load(Mid_O_LogExpSum + offs_logic + block_seq_n)
        new_max_logic = tl.maximum(tlogic, max_logic)

        old_scale = tl.exp(max_logic - new_max_logic)
        acc *= old_scale
        exp_logic = tl.exp(tlogic - new_max_logic)
        acc += exp_logic * tv
        sum_exp = sum_exp * old_scale + exp_logic
        max_logic = new_max_logic

    tl.store(Out + cur_batch * stride_obs + cur_head * stride_oh + offs_d, acc / sum_exp, mask=offs_d < head_dim)
    return

@torch.no_grad()
def flash_decode_stage2(mid_out, mid_out_logexpsum, B_Seqlen, Out, block_seq):
    Lk = mid_out.shape[-1]
    head_dim = Lk
    batch, head_num = mid_out.shape[0], mid_out.shape[1]
    BLOCK_DMODEL = triton.next_power_of_2(head_dim)
    grid = (batch, head_num)

    _fwd_kernel_flash_decode_stage2[grid](
        B_Seqlen,
        mid_out,
        mid_out_logexpsum,
        Out,
        mid_out.stride(0),
        mid_out.stride(1),
        mid_out.stride(2),
        mid_out.stride(3),
        mid_out_logexpsum.stride(0),
        mid_out_logexpsum.stride(1),
        mid_out_logexpsum.stride(2),
        Out.stride(0),
        Out.stride(1),
        Out.stride(2),
        head_dim,
        BLOCK_SEQ=block_seq,
        BLOCK_DMODEL=BLOCK_DMODEL,
        num_warps=4,
        num_stages=2,
    )
    return




##################################################################################################################################################


import torch

# Define the test function
def test_flash_decode_stage2():
    # Define the parameters for different test cases
    batch_size = 2
    head_num = 4
    seq_block_num = 3
    head_dim = 64
    block_seq = 16

    test_cases = {
        "test_case_1": {
            "B_Seqlen": torch.randint(1, seq_block_num * block_seq, (batch_size,), dtype=torch.int32, device='cuda'),
            "mid_out": torch.randn((batch_size, head_num, seq_block_num, head_dim), dtype=torch.float32, device='cuda'),
            "mid_out_logexpsum": torch.randn((batch_size, head_num, seq_block_num), dtype=torch.float32, device='cuda'),
            "Out": torch.zeros((batch_size, head_num, head_dim), dtype=torch.float32, device='cuda'),
            "block_seq": block_seq
        },
        "test_case_2": {
            "B_Seqlen": torch.randint(1, seq_block_num * block_seq, (batch_size,), dtype=torch.int32, device='cuda'),
            "mid_out": torch.randn((batch_size, head_num, seq_block_num, head_dim), dtype=torch.float32, device='cuda'),
            "mid_out_logexpsum": torch.randn((batch_size, head_num, seq_block_num), dtype=torch.float32, device='cuda'),
            "Out": torch.zeros((batch_size, head_num, head_dim), dtype=torch.float32, device='cuda'),
            "block_seq": block_seq + 1  # Different block size
        },
        "test_case_3": {
            "B_Seqlen": torch.randint(1, seq_block_num * block_seq, (batch_size,), dtype=torch.int32, device='cuda'),
            "mid_out": torch.randn((batch_size, head_num, seq_block_num, head_dim), dtype=torch.float32, device='cuda'),
            "mid_out_logexpsum": torch.randn((batch_size, head_num, seq_block_num), dtype=torch.float32, device='cuda'),
            "Out": torch.zeros((batch_size, head_num, head_dim), dtype=torch.float32, device='cuda'),
            "block_seq": block_seq // 2  # Different block size
        },
        "test_case_4": {
            "B_Seqlen": torch.randint(1, seq_block_num * block_seq, (batch_size,), dtype=torch.int32, device='cuda'),
            "mid_out": torch.randn((batch_size, head_num, seq_block_num, head_dim), dtype=torch.float32, device='cuda'),
            "mid_out_logexpsum": torch.randn((batch_size, head_num, seq_block_num), dtype=torch.float32, device='cuda'),
            "Out": torch.zeros((batch_size, head_num, head_dim), dtype=torch.float32, device='cuda'),
            "block_seq": block_seq * 2  # Different block size
        }
    }

    # Execute the function for all test cases
    results = {}
    for key, test_case in test_cases.items():
        flash_decode_stage2(test_case["mid_out"], test_case["mid_out_logexpsum"], test_case["B_Seqlen"], test_case["Out"], test_case["block_seq"])
        results[key] = test_case["Out"]

    return results

# Run the test
result_gold = test_flash_decode_stage2()

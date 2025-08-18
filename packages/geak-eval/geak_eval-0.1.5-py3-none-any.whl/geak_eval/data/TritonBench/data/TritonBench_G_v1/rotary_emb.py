# Modifications Copyright(C)[2025] Advanced Micro Devices, Inc. All rights reserved.
# https://github.com/thunlp/TritonBench - Apache License 2.0
import triton
import triton.language as tl
import torch

@triton.jit
def _rotary_kernel(
    Q,
    K,
    Cos,
    Sin,
    stride_qbs,
    stride_qh,
    stride_qd,
    stride_kbs,
    stride_kh,
    stride_kd,
    stride_cosbs,
    stride_cosd,
    stride_sinbs,
    stride_sind,
    max_total_len,
    HEAD_Q,
    HEAD_K,
    BLOCK_HEAD: tl.constexpr,
    BLOCK_SEQ: tl.constexpr,
    BLOCK_DMODEL: tl.constexpr,
):
    cur_head_index = tl.program_id(0)
    cur_seq_index = tl.program_id(1)

    cur_head_range = cur_head_index * BLOCK_HEAD + tl.arange(0, BLOCK_HEAD)
    cur_seq_range = cur_seq_index * BLOCK_SEQ + tl.arange(0, BLOCK_SEQ)

    dim_range0 = tl.arange(0, BLOCK_DMODEL // 2) * 2
    dim_range1 = tl.arange(0, BLOCK_DMODEL // 2) * 2 + 1

    off_q0 = (
        cur_seq_range[:, None, None] * stride_qbs
        + cur_head_range[None, :, None] * stride_qh
        + dim_range0[None, None, :] * stride_qd
    )
    off_q1 = (
        cur_seq_range[:, None, None] * stride_qbs
        + cur_head_range[None, :, None] * stride_qh
        + dim_range1[None, None, :] * stride_qd
    )

    off_dimcos_sin0 = cur_seq_range[:, None, None] * stride_cosbs + dim_range0[None, None, :] * stride_cosd
    off_dimcos_sin1 = cur_seq_range[:, None, None] * stride_cosbs + dim_range1[None, None, :] * stride_cosd

    q0 = tl.load(
        Q + off_q0,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_Q),
        other=0.0,
    )
    q1 = tl.load(
        Q + off_q1,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_Q),
        other=0.0,
    )

    cos0 = tl.load(Cos + off_dimcos_sin0, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)
    sin0 = tl.load(Sin + off_dimcos_sin0, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)

    cos1 = tl.load(Cos + off_dimcos_sin1, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)
    sin1 = tl.load(Sin + off_dimcos_sin1, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)

    out0 = q0 * cos0 - q1 * sin0
    out1 = q0 * sin1 + q1 * cos1

    tl.store(
        Q + off_q0, out0, mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_Q)
    )
    tl.store(
        Q + off_q1, out1, mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_Q)
    )

    off_k0 = (
        cur_seq_range[:, None, None] * stride_kbs
        + cur_head_range[None, :, None] * stride_kh
        + dim_range0[None, None, :] * stride_kd
    )
    off_k1 = (
        cur_seq_range[:, None, None] * stride_kbs
        + cur_head_range[None, :, None] * stride_kh
        + dim_range1[None, None, :] * stride_kd
    )

    off_dimcos_sin0 = cur_seq_range[:, None, None] * stride_cosbs + dim_range0[None, None, :] * stride_cosd
    off_dimcos_sin1 = cur_seq_range[:, None, None] * stride_cosbs + dim_range1[None, None, :] * stride_cosd

    k0 = tl.load(
        K + off_k0,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_K),
        other=0.0,
    )
    k1 = tl.load(
        K + off_k1,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_K),
        other=0.0,
    )

    cos0 = tl.load(Cos + off_dimcos_sin0, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)
    sin0 = tl.load(Sin + off_dimcos_sin0, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)

    cos1 = tl.load(Cos + off_dimcos_sin1, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)
    sin1 = tl.load(Sin + off_dimcos_sin1, mask=cur_seq_range[:, None, None] < max_total_len, other=0.0)

    out_k0 = k0 * cos0 - k1 * sin0
    out_k1 = k0 * sin1 + k1 * cos1

    tl.store(
        K + off_k0,
        out_k0,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_K),
    )
    tl.store(
        K + off_k1,
        out_k1,
        mask=(cur_seq_range[:, None, None] < max_total_len) & (cur_head_range[None, :, None] < HEAD_K),
    )
    return

@torch.no_grad()
def rotary_emb_fwd(q, k, cos, sin, partial_rotary_factor=1.0):
    total_len = q.shape[0]
    head_num_q, head_num_k = q.shape[1], k.shape[1]
    head_dim = int(q.shape[2] * partial_rotary_factor)
    assert q.shape[0] == cos.shape[0] and q.shape[0] == sin.shape[0], f"q shape {q.shape} cos shape {cos.shape}"
    assert k.shape[0] == cos.shape[0] and k.shape[0] == sin.shape[0], f"k shape {k.shape} cos shape {cos.shape}"

    BLOCK_SEQ = 16
    BLOCK_HEAD = 4
    if head_dim >= 128:
        num_warps = 8
    else:
        num_warps = 4

    grid = (triton.cdiv(head_num_q, BLOCK_HEAD), triton.cdiv(total_len, BLOCK_SEQ))
    _rotary_kernel[grid](
        q,
        k,
        cos,
        sin,
        q.stride(0),
        q.stride(1),
        q.stride(2),
        k.stride(0),
        k.stride(1),
        k.stride(2),
        cos.stride(0),
        cos.stride(1),
        sin.stride(0),
        sin.stride(1),
        total_len,
        head_num_q,
        head_num_k,
        BLOCK_HEAD=BLOCK_HEAD,
        BLOCK_SEQ=BLOCK_SEQ,
        BLOCK_DMODEL=head_dim,
        num_warps=num_warps,
        num_stages=1,
    )
    return




##################################################################################################################################################


import torch

# Define the test function
def test_rotary_emb_fwd():
    # Define the dimensions
    total_len = 32  # Sequence length
    head_num_q = 8  # Number of heads for Q
    head_num_k = 8  # Number of heads for K
    head_dim = 64   # Dimension of each head

    # Create random input tensors
    q = torch.randn((total_len, head_num_q, head_dim), dtype=torch.float32, device='cuda')
    k = torch.randn((total_len, head_num_k, head_dim), dtype=torch.float32, device='cuda')
    cos = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    sin = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')

    # Call the rotary embedding function
    rotary_emb_fwd(q, k, cos, sin)

    # Store the results in a dictionary
    results = {}
    results['test_case_1'] = (q.clone(), k.clone())

    # Additional test cases to cover more branches
    # Test case 2: Different head dimension
    head_dim = 128
    q = torch.randn((total_len, head_num_q, head_dim), dtype=torch.float32, device='cuda')
    k = torch.randn((total_len, head_num_k, head_dim), dtype=torch.float32, device='cuda')
    cos = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    sin = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    rotary_emb_fwd(q, k, cos, sin)
    results['test_case_2'] = (q.clone(), k.clone())

    # Test case 3: Partial rotary factor
    head_dim = 64
    partial_rotary_factor = 0.5
    q = torch.randn((total_len, head_num_q, head_dim), dtype=torch.float32, device='cuda')
    k = torch.randn((total_len, head_num_k, head_dim), dtype=torch.float32, device='cuda')
    cos = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    sin = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    rotary_emb_fwd(q, k, cos, sin, partial_rotary_factor)
    results['test_case_3'] = (q.clone(), k.clone())

    # Test case 4: Different sequence length
    total_len = 64
    q = torch.randn((total_len, head_num_q, head_dim), dtype=torch.float32, device='cuda')
    k = torch.randn((total_len, head_num_k, head_dim), dtype=torch.float32, device='cuda')
    cos = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    sin = torch.randn((total_len, head_dim), dtype=torch.float32, device='cuda')
    rotary_emb_fwd(q, k, cos, sin)
    results['test_case_4'] = (q.clone(), k.clone())

    return results

# Run the test
result_gold = test_rotary_emb_fwd()

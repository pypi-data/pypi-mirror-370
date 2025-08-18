# Modifications Copyright(C)[2025] Advanced Micro Devices, Inc. All rights reserved.
# https://github.com/thunlp/TritonBench - Apache License 2.0
import torch

import triton
import triton.language as tl


@triton.jit
def _fwd_kernel_token_softmax(
    Logics, B_Start_Loc, B_Seqlen,
    Prob_Out,
    stride_logic_h, stride_logic_bs,
    stride_prob_h, stride_prob_bs,
    BLOCK_SIZE: tl.constexpr
):
    cur_batch = tl.program_id(0)
    cur_head = tl.program_id(1)

    col_offsets = tl.arange(0, BLOCK_SIZE)
    cur_batch_seq_len = tl.load(B_Seqlen + cur_batch)
    cur_batch_in_all_start_index = tl.load(B_Start_Loc + cur_batch)

    row = tl.load(Logics + cur_head * stride_logic_h + (cur_batch_in_all_start_index + col_offsets) * stride_logic_bs,
                  mask=col_offsets < cur_batch_seq_len, other=-float('inf')).to(tl.float32)

    row_minus_max = row - tl.max(row, axis=0)
    numerator = tl.exp(row_minus_max)
    denominator = tl.sum(numerator, axis=0)
    softmax_output = numerator / denominator

    tl.store(Prob_Out + cur_head * stride_prob_h + (cur_batch_in_all_start_index + col_offsets)
             * stride_prob_bs, softmax_output, mask=col_offsets < cur_batch_seq_len)
    return


@torch.no_grad()
def token_softmax_fwd(Logics, B_Start_Loc, B_Seqlen, Prob_Out, max_input_len):
    BLOCK_SIZE = triton.next_power_of_2(max_input_len)
    batch, head_num = B_Start_Loc.shape[0], Logics.shape[0]

    num_warps = 4
    if BLOCK_SIZE >= 2048:
        num_warps = 8
    if BLOCK_SIZE >= 4096:
        num_warps = 16

    _fwd_kernel_token_softmax[(batch, head_num)](
        Logics, B_Start_Loc, B_Seqlen,
        Prob_Out,
        Logics.stride(0), Logics.stride(1),
        Prob_Out.stride(0), Prob_Out.stride(1),
        num_warps=num_warps,
        BLOCK_SIZE=BLOCK_SIZE,
    )
    return



##################################################################################################################################################


import torch

def test_token_softmax_fwd():
    results = {}
    
    # Test case 1
    B, N_CTX, H, D = 4, 1025, 12, 128
    dtype = torch.float16
    Logics = torch.empty((H, B * N_CTX), dtype=dtype, device="cuda").normal_(mean=0.1, std=10)
    ProbOut = torch.empty((H, B * N_CTX), dtype=dtype, device="cuda").normal_(mean=0.4, std=0.2)
    b_start_loc = torch.zeros((B,), dtype=torch.int32, device="cuda")
    b_seq_len = torch.zeros((B,), dtype=torch.int32, device="cuda")
    for i in range(B):
        b_start_loc[i] = i * N_CTX
        b_seq_len[i] = N_CTX
    token_softmax_fwd(Logics, b_start_loc, b_seq_len, ProbOut, N_CTX)
    results['test_case_1'] = ProbOut.clone()

    # Test case 2
    B, N_CTX, H, D = 3, 1025, 12, 128
    dtype = torch.float16
    Logics = torch.empty((H, B * N_CTX), dtype=dtype, device="cuda").normal_(mean=0.1, std=10)
    ProbOut = torch.empty((H, B * N_CTX), dtype=dtype, device="cuda").normal_(mean=0.4, std=0.2)
    B = 4
    b_start_loc = torch.zeros((B,), dtype=torch.int32, device="cuda")
    b_seq_len = torch.zeros((B,), dtype=torch.int32, device="cuda")
    b_seq_len[0] = 513
    b_seq_len[1] = 1025
    b_seq_len[2] = 513
    b_seq_len[3] = 1024
    for i in range(1, B):
        b_start_loc[i] = b_start_loc[i - 1] + b_seq_len[i - 1]
    token_softmax_fwd(Logics, b_start_loc, b_seq_len, ProbOut, N_CTX)
    results['test_case_2'] = ProbOut.clone()

    return results

result_gold = test_token_softmax_fwd()

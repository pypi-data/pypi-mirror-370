# Copyright(C) [2025] Advanced Micro Devices, Inc. All rights reserved.
####################### Imports #####################
import argparse
import torch
import sys
import pytest
from itertools import product

import triton
import triton.language as tl
####################### Imports #####################



@triton.jit
def rms_bwd_kernel(grad_output_ptr, input_ptr, g_ptr, rsigma_ptr, dx_ptr, dg_ptr, input_row_stride, output_row_stride,
                   n_rows, n_cols, ZERO_CENTERED_GAMMA: tl.constexpr, BLOCK_SIZE: tl.constexpr,
                   USE_BLOCKED: tl.constexpr, NUM_PRGMS: tl.constexpr):
    row_start = tl.program_id(0)
    col_offsets = tl.arange(0, BLOCK_SIZE)
    #   tl.assume(input_row_stride >= 0)
    #   tl.assume(output_row_stride >= 0)
    #   tl.assume(row_start >= 0)

    if USE_BLOCKED:
        for row_idx in tl.range(row_start, n_rows, NUM_PRGMS, num_stages=1):
            row_input_ptr = input_ptr + row_idx * input_row_stride
            row_grad_output_ptr = grad_output_ptr + row_idx * output_row_stride
            row_dx_ptr = dx_ptr + row_idx * input_row_stride
            row_dg_ptr = dg_ptr + row_idx * input_row_stride

            # Compute gradients sum of all colums for each row
            n_cols_blks = tl.cdiv(n_cols, BLOCK_SIZE) - 1
            # older version of triton doesn't accept below init
            # comment out for now to make it compatible with triton 3.1
            # grad_sum: tl.float32 = 0.0
            grad_sum = 0.0
            for blk_idx in tl.range(0, n_cols_blks, num_stages=2):
                cols = blk_idx * BLOCK_SIZE + col_offsets
                input_ptrs = row_input_ptr + cols
                grad_output_ptrs = row_grad_output_ptr + cols

                input_ptrs = tl.multiple_of(input_ptrs, (16, ))
                grad_output_ptrs = tl.multiple_of(grad_output_ptrs, (16, ))

                x = tl.load(input_ptrs).to(tl.float32)
                grad_output = tl.load(grad_output_ptrs).to(tl.float32)
                g_ptrs = g_ptr + cols
                g = tl.load(g_ptrs).to(tl.float32)
                if (ZERO_CENTERED_GAMMA):
                    g += 1.
                grad_sum += tl.sum(grad_output * x * g, axis=0)

            # remainder for grad_sum:
            cols = n_cols_blks * BLOCK_SIZE + col_offsets
            mask = cols < n_cols
            input_ptrs = row_input_ptr + cols
            x = tl.load(input_ptrs, mask=mask, other=0.0).to(tl.float32)
            grad_output_ptrs = row_grad_output_ptr + cols
            grad_output = tl.load(grad_output_ptrs, mask=mask, other=0.0).to(tl.float32)
            g_ptrs = g_ptr + cols
            g = tl.load(g_ptrs, mask=mask, other=0.0).to(tl.float32)
            if (ZERO_CENTERED_GAMMA):
                g += 1.
            grad_sum += tl.sum(grad_output * x * g, axis=0)

            # Load r_sigma
            norm_factor = tl.load(rsigma_ptr + row_idx).to(tl.float32)

            for blk_idx in tl.range(0, n_cols_blks, num_stages=2):
                cols = blk_idx * BLOCK_SIZE + col_offsets
                input_ptrs = row_input_ptr + cols
                grad_output_ptrs = row_grad_output_ptr + cols

                input_ptrs = tl.multiple_of(input_ptrs, (16, ))
                grad_output_ptrs = tl.multiple_of(grad_output_ptrs, (16, ))

                x = tl.load(input_ptrs).to(tl.float32)
                grad_output = tl.load(grad_output_ptrs).to(tl.float32)

                g_ptrs = g_ptr + cols
                g = tl.load(g_ptrs).to(tl.float32)
                if (ZERO_CENTERED_GAMMA):
                    g += 1.
                grad_input = grad_output * norm_factor * g - (norm_factor * norm_factor * norm_factor) * x * (grad_sum /
                                                                                                              n_cols)

                dx_ptrs = row_dx_ptr + cols
                tl.store(dx_ptrs, grad_input.to(dx_ptr.type.element_ty))

                dg = grad_output * x * norm_factor
                dg_ptrs = row_dg_ptr + cols
                tl.store(dg_ptrs, dg.to(tl.float32))

            # Handle remainder
            cols = n_cols_blks * BLOCK_SIZE + col_offsets
            mask = cols < n_cols

            input_ptrs = row_input_ptr + cols
            x = tl.load(input_ptrs, mask=mask, other=0.0).to(tl.float32)
            grad_output_ptrs = row_grad_output_ptr + cols
            grad_output = tl.load(grad_output_ptrs, mask=mask, other=0.0).to(tl.float32)
            g_ptrs = g_ptr + cols
            g = tl.load(g_ptrs, mask=mask, other=0.0).to(tl.float32)
            if (ZERO_CENTERED_GAMMA):
                g += 1.
            grad_input = grad_output * norm_factor * g - (norm_factor * norm_factor * norm_factor) * x * (grad_sum /
                                                                                                          n_cols)

            dx_ptrs = row_dx_ptr + cols
            tl.store(dx_ptrs, grad_input.to(dx_ptr.type.element_ty), mask=mask)

            dg = grad_output * x * norm_factor
            dg_ptrs = row_dg_ptr + cols
            tl.store(dg_ptrs, dg.to(tl.float32), mask=mask)

    else:
        mask = col_offsets < n_cols
        for row_idx in tl.range(row_start, n_rows, NUM_PRGMS, num_stages=2):
            input_ptrs = input_ptr + row_idx * input_row_stride + col_offsets
            grad_output_ptrs = grad_output_ptr + row_idx * output_row_stride + col_offsets
            dx_ptrs = dx_ptr + row_idx * input_row_stride + col_offsets
            dg_ptrs = dg_ptr + row_idx * input_row_stride + col_offsets

            input_ptrs = tl.multiple_of(input_ptrs, (16, ))
            grad_output_ptrs = tl.multiple_of(grad_output_ptrs, (16, ))
            dx_ptrs = tl.multiple_of(dx_ptrs, (16, ))

            x = tl.load(input_ptrs, mask=mask, other=0.0).to(tl.float32)
            grad_output = tl.load(grad_output_ptrs, mask=mask, other=0.0).to(tl.float32)
            g = tl.load(g_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            if (ZERO_CENTERED_GAMMA):
                g += 1.

            norm_factor = tl.load(rsigma_ptr + row_idx).to(tl.float32)
            grad_sum = tl.sum(grad_output * x * g, axis=0)

            grad_input = grad_output * norm_factor * g - (norm_factor * norm_factor * norm_factor) * x * (grad_sum /
                                                                                                          n_cols)
            tl.store(dx_ptrs, grad_input.to(dx_ptr.type.element_ty), mask=mask)

            dg = grad_output * x * norm_factor
            tl.store(dg_ptrs, dg.to(tl.float32), mask=mask)





##################################################################################################################################################

######################################## HELPERS for Eval ######################################## 
import numpy as np
import random
import torch 
import os
import argparse
import sys
import pytest
from itertools import product
from geak_eval.perf.ROCm.performance_utils_pytest import PytestBenchmarker, do_bench_config, save_all_benchmark_results
from typing import Dict

import triton
import triton.language as tl
  

result_gold = {}
CONFIG = {
  "llama3": {
    "8B": {
      "num_attention_heads": 32,
      "num_key_value_heads": 8,
      "hidden_size": 4096,
      "intermediate_size": 14336,
      "vocab_size": 128256
    },
    "70B": {
      "num_attention_heads": 64,
      "num_key_value_heads": 8,
      "hidden_size": 8192,
      "intermediate_size": 28672,
      "vocab_size": 128256
    },
    "405B": {
      "num_attention_heads": 128,
      "num_key_value_heads": 8,
      "hidden_size": 16384,
      "intermediate_size": 53248,
      "vocab_size": 128256
    }
  },
  "mistral": {
    "7B": {
      "hidden_size": 4096,
      "intermediate_size": 14336,
      "num_attention_heads": 32,
      "num_key_value_heads": 8,
      "vocab_size": 32000
    },
    "22B": {
      "hidden_size": 6144,
      "intermediate_size": 16384,
      "num_attention_heads": 48,
      "num_key_value_heads": 8,
      "vocab_size": 32000
    }

  }
}

  
def get_model_configs(config_path='model_configs.json', model_families=["llama3"], model="all"):  
    """  
    Load model names from the configuration file.  
  
    Args:  
        config_path (str): User-provided path to the configuration JSON file.  
        model_families (list): List of model family names to retrieve.  
  
    Returns:  
        dict: A dictionary of available models and their configurations for the specified families.  
    """  
    configs = CONFIG.copy()
  
    # Extract models and their configurations for the specified families  
    filtered_configs = {}  
  
    for family in model_families:  
        if family in configs:  
            # Check if model filtering is required  
            if model == "all":  
                # Include all models in the family  
                for model_size, model_configs in configs[family].items():  
                    filtered_configs[f"{family}-{model_size}"] = model_configs  
            else:  
                # Parse the model string (e.g., llama3_8B or llama3-8B)  
                delimiter = "_" if "_" in model else "-"  
                model_parts = model.split(delimiter)  
  
                # Check if the family and size match  
                if len(model_parts) == 2 and model_parts[0] == family:  
                    model_size = model_parts[1]  
                    if model_size in configs[family]:  
                        filtered_configs[f"{family}-{model_size}"] = configs[family][model_size]  
  
    if not filtered_configs:  
        print(f"Warning: No models selected for families: {model_families} with filter: '{model}'")  
  
    return filtered_configs  
  
  
def get_available_models(config_file='model_configs.json', model_families=["llama3"]):  
    """  
    Load model names from the configuration file.  
  
    Args:  
        config_file (str): Path to the configuration JSON file.  
        model_families (list): List of model family names to retrieve.  
  
    Returns:  
        list: A list of available models for the specified families.  
    """  
    configs = CONFIG.copy()
  
    models = [f"{family}-{model}" for family in model_families if family in configs for model in configs[family]]  
  
    return models  


def set_seed(seed: int = 42) -> None:
    """
    Set the random seed for reproducibility across multiple libraries and configure PyTorch for deterministic behavior.

    Args:
        seed (int): The seed value to set. Default is 42.
    """
    # Set seed for Python's built-in random module
    random.seed(seed)
    # Set seed for NumPy
    np.random.seed(seed)
    # Set seed for PyTorch on CPU
    torch.manual_seed(seed)
    # Set seed for PyTorch on all GPUs (if available)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    # Ensure deterministic behavior in PyTorch
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    # Set environment variable for hash-based operations
    os.environ['PYTHONHASHSEED'] = str(seed)

######################################## HELPERS for Eval ######################################## 

############################ HELPER utils ############################


def is_cuda():
    return triton.runtime.driver.active.get_current_target().backend == "cuda"


def is_hip():
    return triton.runtime.driver.active.get_current_target().backend == "hip"


def get_num_sms():
    current_device_index = torch.cuda.current_device()
    current_device = torch.cuda.get_device_properties(current_device_index)
    num_sms = current_device.multi_processor_count
    return num_sms


def get_cuda_autotune_config():
    return [
        triton.Config({}, num_warps=4, num_stages=1),
        triton.Config({}, num_warps=8, num_stages=1),
        triton.Config({}, num_warps=16, num_stages=1),
    ]


def get_hip_autotune_config():
    return [triton.Config({'waves_per_eu': we}, num_warps=nw) for (we, nw) in product([0, 1, 2, 4], [4, 8, 16])]


def get_autotune_config():
    if is_cuda():
        return get_cuda_autotune_config()
    else:
        return get_hip_autotune_config()
############################ HELPER utils ############################
@triton.autotune(configs=get_autotune_config(), key=['n_rows', 'n_cols'], use_cuda_graph=True)
@triton.jit
def rms_kernel(output_ptr, input_ptr, g_ptr, rsigma_ptr, input_row_stride, output_row_stride, n_rows, n_cols, epsilon,
               ZERO_CENTERED_GAMMA: tl.constexpr, BLOCK_SIZE: tl.constexpr, USE_BLOCKED: tl.constexpr,
               NUM_PRGMS: tl.constexpr):
    row_start = tl.program_id(0)
    col_offsets = tl.arange(0, BLOCK_SIZE)
    # as older version Triton doesn't support tl.assume and BUFF OPS, comment out for now
    # tl.assume(input_row_stride >= 0)
    # tl.assume(output_row_stride >= 0)
    # tl.assume(row_start >= 0)

    if USE_BLOCKED:

        # Persistent loop for rows
        for row_idx in tl.range(row_start, n_rows, NUM_PRGMS, num_stages=1):
            row_input_ptr = input_ptr + row_idx * input_row_stride
            row_output_ptr = output_ptr + row_idx * output_row_stride

            # Accumulate sum of squares
            n_cols_blks = tl.cdiv(n_cols, BLOCK_SIZE) - 1
            # older version of triton doesn't accept below init
            # sum_squares: tl.float32 = 0.
            # however, with type promoting rule in triton, sum_squares should be always fp32 with below init
            sum_squares = 0.
            for blk_idx in tl.range(0, n_cols_blks, num_stages=2):
                cols = blk_idx * BLOCK_SIZE + col_offsets
                input_ptrs = row_input_ptr + cols
                input_ptrs = tl.multiple_of(input_ptrs, (16, ))
                x = tl.load(input_ptrs).to(tl.float32)
                sum_squares += tl.sum(x * x, axis=0)

            # Handle remainder
            cols = n_cols_blks * BLOCK_SIZE + col_offsets
            mask = cols < n_cols
            input_ptrs = row_input_ptr + cols
            input_ptrs = tl.multiple_of(input_ptrs, (16, ))
            x = tl.load(input_ptrs, mask=mask, other=0.0, cache_modifier=".cg").to(tl.float32)
            sum_squares += tl.sum(x * x, axis=0)

            # Compute normalization factor
            mean_square = sum_squares / n_cols
            norm_factor = tl.rsqrt(mean_square + epsilon)

            # Store rsigma (norm_factor)
            tl.store(rsigma_ptr + row_idx, norm_factor)

            # Normalize and write output
            for blk_idx in tl.range(0, n_cols_blks, num_stages=2):
                cols = blk_idx * BLOCK_SIZE + col_offsets
                input_ptrs = row_input_ptr + cols
                input_ptrs = tl.multiple_of(input_ptrs, (16, ))
                x = tl.load(input_ptrs).to(tl.float32)
                g_ptrs = g_ptr + cols
                g = tl.load(g_ptrs).to(tl.float32)
                if (ZERO_CENTERED_GAMMA):
                    g += 1
                rms_norm = x * norm_factor * g
                output_ptrs = row_output_ptr + cols
                tl.store(output_ptrs, rms_norm.to(output_ptr.type.element_ty))

            # Handle remainder
            cols = n_cols_blks * BLOCK_SIZE + col_offsets
            mask = cols < n_cols
            input_ptrs = row_input_ptr + cols
            x = tl.load(input_ptrs, mask=mask, other=0.0, cache_modifier=".cg").to(tl.float32)
            g_ptrs = g_ptr + cols
            g = tl.load(g_ptrs, mask=mask, other=0.0).to(tl.float32)
            if (ZERO_CENTERED_GAMMA):
                g += 1
            rms_norm = x * norm_factor * g
            output_ptrs = row_output_ptr + cols
            tl.store(output_ptrs, rms_norm.to(output_ptr.type.element_ty), mask=mask)

    else:
        mask = col_offsets < n_cols
        for row_idx in tl.range(row_start, n_rows, NUM_PRGMS, num_stages=2):
            input_ptrs = input_ptr + row_idx * input_row_stride + col_offsets
            input_ptrs = tl.multiple_of(input_ptrs, (16, ))
            row = tl.load(input_ptrs, mask=mask, other=0.0, cache_modifier=".cg").to(tl.float32)
            g = tl.load(g_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            row_norm = row * row
            row_norm = tl.sum(row_norm, axis=-1)
            norm_factor = tl.math.rsqrt((row_norm / n_cols) + epsilon)

            # Store rsigma (norm_factor)
            rsigma_output_ptr = rsigma_ptr + row_idx
            tl.store(rsigma_output_ptr, norm_factor)

            if (ZERO_CENTERED_GAMMA):
                g += 1
            rms_norm = row * norm_factor * g

            output_ptrs = output_ptr + row_idx * output_row_stride + col_offsets
            output_ptrs = tl.multiple_of(output_ptrs, (16, ))
            tl.store(output_ptrs, rms_norm.to(output_ptr.type.element_ty), mask=mask)



@triton.jit
def _rmsnorm_bwd_dg_reduce(dg_in_ptr, dg_out_ptr, dg_in_stride, n_rows, n_cols, BLOCK_SIZE_M: tl.constexpr,
                           BLOCK_SIZE_N: tl.constexpr):
    # we want parallelism in N direction
    # if N is small, we will just use one CU,
    # otherwise, it can be split by N/BLOCK_SIZE
    pid = tl.program_id(0)
    cols = pid * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)
    acc = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)
    for i in range(0, n_rows, BLOCK_SIZE_M):
        rows = i + tl.arange(0, BLOCK_SIZE_M)
        mask = (rows[:, None] < n_rows) & (cols[None, :] < n_cols)
        offs = rows[:, None] * n_cols + cols[None, :]
        acc += tl.load(dg_in_ptr + offs, mask=mask, other=0.).to(tl.float32)

    sum_dg = tl.sum(acc, axis=0)
    tl.store(dg_out_ptr + cols, sum_dg.to(dg_out_ptr.type.element_ty), mask=cols < n_cols)


class RMSNorm(torch.autograd.Function):

    @staticmethod
    def forward(ctx, x, g, y, rsigma, dx, dg, dg_tmp, n_rows, n_cols, ZERO_CENTERED_GAMMA, blk_size, USE_BLOCKED,
                NUM_PRGMS, epsilon=1e-6):
        # heuristics for number of warps
        #    num_warps = min(max(blk_size // 256, 1), 8)
        num_warps = 8
        grid = lambda meta: (NUM_PRGMS, )
        rms_kernel[grid](y, x, g, rsigma, x.stride(0), y.stride(0), n_rows, n_cols, epsilon, ZERO_CENTERED_GAMMA,
                         blk_size, USE_BLOCKED, NUM_PRGMS)

        ctx.save_for_backward(x, g, rsigma)
        ctx.n_rows = n_rows
        ctx.n_cols = n_cols
        ctx.ZERO_CENTERED_GAMMA = ZERO_CENTERED_GAMMA
        ctx.blk_size = blk_size
        ctx.USE_BLOCKED = USE_BLOCKED
        ctx.NUM_PRGMS = NUM_PRGMS
        ctx.num_warps = num_warps

        ctx.dx = dx
        ctx.dg_tmp = dg_tmp
        ctx.dg = dg

        return y

    @staticmethod
    def backward(ctx, grad_output):
        x, g, rsigma = ctx.saved_tensors
        dg_tmp = ctx.dg_tmp
        dx = ctx.dx
        dg = ctx.dg
        n_rows = ctx.n_rows
        n_cols = ctx.n_cols
        ZERO_CENTERED_GAMMA = ctx.ZERO_CENTERED_GAMMA
        blk_size = ctx.blk_size
        USE_BLOCKED = ctx.USE_BLOCKED
        NUM_PRGMS = ctx.NUM_PRGMS

        grid_bwd = lambda meta: (NUM_PRGMS, )
        rms_bwd_kernel[grid_bwd](grad_output, x, g, rsigma, dx, dg_tmp, x.stride(0), grad_output.stride(0), n_rows,
                                 n_cols, ZERO_CENTERED_GAMMA, blk_size, USE_BLOCKED, NUM_PRGMS, num_warps=ctx.num_warps)

        #        grid_reduce = lambda meta: (triton.cdiv(n_cols, blk_size), )
        grid_reduce = lambda meta: [triton.cdiv(n_cols, meta['BLOCK_SIZE_N'])]
        _rmsnorm_bwd_dg_reduce[grid_reduce](dg_tmp, dg, dg_tmp.stride(0), n_rows, n_cols, BLOCK_SIZE_M=128,
                                            BLOCK_SIZE_N=64)

        return dx, dg, None, None, None, None, None, None, None, None, None, None, None


rmsnorm = RMSNorm.apply


def torch_rmsnorm_fwd(x, g, ZERO_CENTERED_GAMMA, out_dtype=torch.float16, epsilon=1e-6):
    M, N = x.shape
    # cast to float32 as the triton kernel
    x_f32 = x.float()
    g_f32 = g.float()
    rms = torch.sqrt(torch.sum(x_f32 * x_f32, dim=-1) * 1 / N)
    rsigma = 1.0 / rms
    if (ZERO_CENTERED_GAMMA):
        g_f32 = g_f32 + 1
    rms_norm_f32 = x_f32 * rsigma.unsqueeze(1) * g_f32
    rms_norm = rms_norm_f32.to(out_dtype)
    return rms_norm, rsigma


arg_to_torch_dtype = {'fp16': torch.float16, 'bf16': torch.bfloat16, 'fp32': torch.float32}


    # (8192, 65536),

#@pytest.mark.parametrize("in_dtype_str", ["fp32", "fp16", "bf16"])
#@pytest.mark.parametrize("out_dtype_str", ["fp32", "fp16", "bf16"])
@pytest.mark.parametrize("in_dtype_str", ["fp16", "bf16"])
@pytest.mark.parametrize("out_dtype_str", ["fp16", "bf16"])
@pytest.mark.parametrize('ZERO_CENTERED_GAMMA', [True, False])
@pytest.mark.parametrize('M, N', [
    (1, 4),
    (2, 10),
    (256, 4096),
    (1, 31744),
    (873, 1245),
])
def test_rmsnorm(M, N, ZERO_CENTERED_GAMMA, in_dtype_str, out_dtype_str, request):
    in_dtype = arg_to_torch_dtype[in_dtype_str]
    out_dtype = arg_to_torch_dtype[out_dtype_str]
    set_seed()

    x = torch.randn(M, N, device='cuda', dtype=in_dtype, requires_grad=True)
    g = torch.ones((1, N), device='cuda', dtype=in_dtype, requires_grad=True)
    y = torch.zeros_like(x, device='cuda', dtype=out_dtype)
    rsigma = torch.empty((M, ), device=x.device, dtype=torch.float32)

    dx = torch.empty_like(x, dtype=in_dtype, requires_grad=False)
    dg = torch.empty_like(g, dtype=in_dtype, requires_grad=False)
    dg_tmp = torch.zeros(M, N, device='cuda', dtype=torch.float32, requires_grad=False)

    n_rows, n_cols = x.shape
    MAX_FUSED_SIZE = 65536 // x.element_size()
    blk_size = min(MAX_FUSED_SIZE, triton.next_power_of_2(n_cols))
    USE_BLOCKED = n_cols > blk_size
    NUM_PRGMS = min(n_rows, get_num_sms())

    y_triton = rmsnorm(x, g, y, rsigma, dx, dg, dg_tmp, n_rows, n_cols, ZERO_CENTERED_GAMMA, blk_size, USE_BLOCKED,
                       NUM_PRGMS)

    y_torch, rsigma_torch = torch_rmsnorm_fwd(x, g, ZERO_CENTERED_GAMMA, out_dtype)

    if out_dtype in (torch.float16, torch.bfloat16):
        atol, rtol = 1e-3, 1e-2
    else:
        # float32 typically can be tighter
        atol, rtol = 1e-5, 1e-5

    result_gold['_CALL_SUCCESS_'] = torch.tensor([[1.0]])
    
    assert y_triton.dtype == out_dtype, f"y_triton has dtype={y_triton.dtype}, expected {out_dtype}"
    assert y_torch.dtype == out_dtype, f"y_torch has dtype={y_torch.dtype}, expected {out_dtype}"

    assert torch.allclose(y_triton, y_torch, atol=atol, rtol=rtol), \
        f"Mismatch in 'y' (in={in_dtype_str}, out={out_dtype_str})"
    assert torch.allclose(rsigma, rsigma_torch, atol=atol, rtol=rtol), \
        f"Mismatch in 'rsigma' (in={in_dtype_str}, out={out_dtype_str})"

    grad_output = torch.randn_like(y_torch)

    # 1) PyTorch reference backward
    # We must clone and set requires_grad = True for backward
    x_ref = x.clone().detach().requires_grad_()
    g_ref = g.clone().detach().requires_grad_()
    y_ref, rsigma_ref = torch_rmsnorm_fwd(x_ref, g_ref, ZERO_CENTERED_GAMMA, out_dtype)

    # Backpropagate through PyTorch
    y_ref.backward(grad_output)
    grad_x_ref = x_ref.grad.to(out_dtype)
    grad_g_ref = g_ref.grad.to(out_dtype)

    # 2) Triton backward
    x_triton = x.clone().detach().requires_grad_()
    g_triton = g.clone().detach().requires_grad_()

    y_triton_buf = torch.empty_like(x_triton, dtype=out_dtype)
    rsigma_triton = torch.empty((M, ), device=x_triton.device, dtype=torch.float32)

    dx_b = torch.empty_like(x_triton, dtype=in_dtype, requires_grad=False)
    dg_b = torch.empty_like(g_triton, dtype=in_dtype, requires_grad=False)
    dg_tmp_b = torch.zeros(M, N, device=x_triton.device, dtype=torch.float32, requires_grad=False)

    # Run Triton forward pass to build the graph for backward.
    y_triton = rmsnorm(x_triton, g_triton, y_triton_buf, rsigma_triton, dx_b, dg_b, dg_tmp_b, n_rows, n_cols,
                       ZERO_CENTERED_GAMMA, blk_size, USE_BLOCKED, NUM_PRGMS)
    y_triton.backward(grad_output, retain_graph=True)
    grad_x_triton = x_triton.grad.to(out_dtype)
    grad_g_triton = g_triton.grad.to(out_dtype)

    # Compare backward outputs (grad_x and grad_g)
    err_x = (grad_x_triton - grad_x_ref).abs().max().item()


    ################### save grad_x_triton, grad_g_triton in result_gold ###################
    test_case_name = request.node.name
    sanitized_key_name = test_case_name.replace("::", "_").replace("[", "_").replace("]", "").replace("-", "_") + "_grad_x_triton"
    result_gold[sanitized_key_name] = grad_x_triton.clone().detach().cpu()

    sanitized_key_name = test_case_name.replace("::", "_").replace("[", "_").replace("]", "").replace("-", "_") + "_grad_g_triton"
    result_gold[sanitized_key_name] = grad_g_triton.clone().detach().cpu()
    ################################################################### 


    assert torch.allclose(grad_x_triton, grad_x_ref, atol=atol, rtol=rtol), \
    f"Triton dx mismatch (max error: {err_x:.4e})\n\n"
    f"Triton grad x:\n{grad_x_triton}\n\nPyTorch grad_x:\n{grad_x_ref}"

    err_g = (grad_g_triton - grad_g_ref).abs().max().item()
    assert torch.allclose(grad_g_triton, grad_g_ref, atol=atol, rtol=rtol), \
    f"Triton dg mismatch (max error: {err_g:.4e})\n\n"
    f"Triton grad g:\n{grad_g_triton}\n\nPyTorch grad_g:\n{grad_g_ref}"


# --- Define TFLOPS and GB/s calculators for RMSNorm Forward ---
def calculate_rmsnorm_fwd_gbps(params: dict, ms: float) -> float:
    M, N = params['M'], params['N']
    dtype_str = params.get('dtype_str', 'fp16')
    if dtype_str == 'fp32': current_dtype = torch.float32
    elif dtype_str == 'bf16': current_dtype = torch.bfloat16
    else: current_dtype = torch.float16
    element_size = torch.tensor([], dtype=current_dtype).element_size()
    
    # Read x (M,N), g (N)
    # Write y (M,N), rsigma (M)
    bytes_read_x = M * N * element_size
    bytes_read_g = N * element_size
    bytes_write_y = M * N * element_size
    bytes_write_rsigma = M * 4 # rsigma is usually float32

    total_bytes = bytes_read_x + bytes_read_g + bytes_write_y + bytes_write_rsigma
    gbps = total_bytes / (ms / 1000) / 1e9
    return gbps

def calculate_rmsnorm_fwd_tflops(params: dict, ms: float) -> float:
    M, N = params['M'], params['N']
    # FLOPs for RMSNorm forward:
    # 1. Sum of squares: N squares, N-1 additions per row (2N-1 ops)
    # 2. Mean square: 1 division per row (1 op)
    # 3. rsqrt: (approx ~5-10 ops, let's say 5)
    # 4. Normalize & Scale: N mult (x*rsigma), N mult (*g) per row (2N ops)
    # (If ZERO_CENTERED_GAMMA, N additions for g = g+1)
    # Total per row approx: (2N-1) + 1 + 5 + 2N = 4N + 5 ops
    # If ZERO_CENTERED_GAMMA: add N ops => 5N + 5
    flops_per_row = 4 * N + 5
    if params.get('ZERO_CENTERED_GAMMA', False):
        flops_per_row += N
    total_flops = M * flops_per_row
    tflops = total_flops / (ms / 1000) / 1e12
    return tflops

# --- Name for the benchmark output JSON file ---
OP_NAME_FOR_BENCHMARK = "rmsnorm_triton_bwd_perf"

# --- Pytest parametrize for performance testing ---
RMSNORM_SHAPES_FOR_PERF = [
    (256, 4096), (2048, 2048), (4096, 8192), (8192, 8192),
    (1, 31744), (1, 131072),
    (512, 10240) # Typical LLM shape
]
RMSNORM_DTYPES_FOR_PERF = ['fp16', 'bf16', 'fp32']

@pytest.mark.parametrize('M, N', RMSNORM_SHAPES_FOR_PERF)
@pytest.mark.parametrize('dtype_str', RMSNORM_DTYPES_FOR_PERF)
@pytest.mark.parametrize('ZERO_CENTERED_GAMMA', [False, True]) # Test both gamma modes
def test_performance(M, N, ZERO_CENTERED_GAMMA, dtype_str, request):
    set_seed()
    eps = 1e-5

    if dtype_str == 'fp32': current_dtype = torch.float32
    elif dtype_str == 'bf16': current_dtype = torch.bfloat16
    else: current_dtype = torch.float16

    # Prepare inputs and output buffers for RMSNorm.apply
    x = torch.randn(M, N, device='cuda', dtype=current_dtype)
    g = torch.rand(N, device='cuda', dtype=current_dtype) # Original test_rmsnorm used (1,N)
                                                       # Kernel expects g_ptr + col_offsets, so 1D g is fine.
    y_buffer = torch.empty_like(x) # Output buffer for forward
    rsigma_buffer = torch.empty(M, device='cuda', dtype=torch.float32) # rsigma output

    # Dummy buffers for backward context (not used by fwd pass, but part of RMSNorm.apply signature)
    # Their dtypes should match what backward pass would expect if it were called.
    dx_dummy = torch.empty_like(x)
    dg_dummy = torch.empty_like(g)
    dg_tmp_dummy = torch.empty(M, N, device='cuda', dtype=torch.float32) # As per original test_rmsnorm

    # Kernel launch parameters (from original test_rmsnorm)
    n_rows, n_cols = x.shape
    MAX_FUSED_SIZE = 65536 // x.element_size()
    # Ensure blk_size is at least 1, next_power_of_2(0) or small N can be problematic
    blk_size_fwd = min(MAX_FUSED_SIZE, triton.next_power_of_2(n_cols if n_cols > 0 else 1))
    if blk_size_fwd == 0 : blk_size_fwd = 1 # Safeguard
    
    USE_BLOCKED_fwd = n_cols > blk_size_fwd
    # NUM_PRGMS should be > 0
    NUM_PRGMS_fwd = min(n_rows, get_num_sms()) if n_rows > 0 and get_num_sms() > 0 else 1


    # --- Create op_lambda for benchmarking the forward pass ---
    op_lambda = lambda: rmsnorm(
        x, g, y_buffer, rsigma_buffer,
        dx_dummy, dg_dummy, dg_tmp_dummy,
        n_rows, n_cols, ZERO_CENTERED_GAMMA,
        blk_size_fwd, USE_BLOCKED_fwd, NUM_PRGMS_fwd, eps
    )

    # --- Benchmarking ---
    bench_config = do_bench_config(warm_up=25, repetition=100)
    benchmarker = PytestBenchmarker(op_callable=op_lambda,
                                    op_name=OP_NAME_FOR_BENCHMARK,
                                    config=bench_config)

    current_params_for_logs_and_calc = {
        "M": M, "N": N, "ZERO_CENTERED_GAMMA": ZERO_CENTERED_GAMMA,
        "dtype_str": dtype_str, "eps": eps,
        "blk_size_fwd": blk_size_fwd, "USE_BLOCKED_fwd": USE_BLOCKED_fwd, "NUM_PRGMS_fwd": NUM_PRGMS_fwd
    }

    benchmarker.run_benchmark(current_params_dict=current_params_for_logs_and_calc,
                              gbps_calculator=calculate_rmsnorm_fwd_gbps,
                              tflops_calculator=calculate_rmsnorm_fwd_tflops)
    
######################################## HELPERS for Eval ########################################     
# --- Pytest hook to save the dictionary at the end of the session ---  
def test_save_results():  
    """  
    Called after whole test run finished, right before returning the exit status to the system.  
    """
    print('Inside session finish...')
    if "_CALL_SUCCESS_" not in result_gold:
        result_gold['_CALL_SUCCESS_'] = torch.tensor([[0.0]])
    OUTPUT_FILENAME = __file__.replace('.','_') + '.pt'
    print(f"\nSaving all y_triton results to {OUTPUT_FILENAME}...")  
    # Ensure the directory for the output file exists if it's in a subdirectory  
    output_dir = os.path.dirname(OUTPUT_FILENAME)  
    if output_dir and not os.path.exists(output_dir):  
        os.makedirs(output_dir, exist_ok=True)  
    torch.save(result_gold, OUTPUT_FILENAME)       
    print(f"Successfully saved {len(result_gold)} y_triton tensors to {OUTPUT_FILENAME}.")  


def test_save_performance_results():
    """
    Called after the test_performance function finishes.
    This is a separate hook to ensure performance results are saved.
    """
    print('\nPytest session finishing... Saving benchmark results...')

    output_directory = os.path.join(os.path.dirname(__file__), "perf")  # Save in a "perf" subdirectory next to the test file
    os.makedirs(output_directory, exist_ok=True)
    
    save_all_benchmark_results(output_directory)
    print(f"All benchmark results attempted to save to: {output_directory}")
    
######################################## HELPERS for Eval ########################################


#Benchmark
def model_benchmark_configs(args):
    config_file = args.model_configs
    configs = get_model_configs(config_path=config_file, model_families=["llama3"], model=args.model)

    x_vals_list = []
    batch_size = args.b if args.b else 1

    for model_name, config in configs.items():
        seq_len = args.sq if args.sq else 4096
        x_vals_list.append((model_name, batch_size * seq_len, config["hidden_size"]))

    return x_vals_list


def run_benchmark(args):
    config = []
    if (args.M_benchmark):
        val = args.M_start
        x_vals_list = []
        while val <= args.M_end:
            x_vals_list.append(val)
            val *= args.M_step
        mn_args = {'N': args.N_start}
        plot_name = str("rmsnorm-performance_" + args.dtype + "_N" + str(args.N_start) + "_M" + str(args.M_start) +
                        "-" + str(args.M_end) + "-" + str(args.M_step))
        x_names = ['M']
    else:
        x_vals_list = [i for i in range(args.N_start, args.N_end, args.N_step)]
        mn_args = {'M': args.M_start}
        x_names = ['N']
        plot_name = str("rmsnorm-performance_" + args.dtype + "_M" + str(args.M_start) + "_N" + str(args.N_start) +
                        "-" + str(args.N_end) + "-" + str(args.N_step))

    if args.model:
        assert not args.M_benchmark, \
            "Trying to provide both -model benchmark and M_benchmark is not supported!"
        x_names = ['model', 'M', 'N']
        mn_args = {}
        plot_name = str("rmsnorm-performance_" + args.dtype)
        x_vals_list = model_benchmark_configs(args)

    dtype = arg_to_torch_dtype[args.dtype]

    print(plot_name)
    config.append(
        triton.testing.Benchmark(
            x_names=x_names,
            x_vals=x_vals_list,
            line_arg='provider',
            line_vals=['triton', 'torch'],
            line_names=["Triton", "Torch"],
            styles=[('blue', '-'), ('green', '-')],
            ylabel="GB/s",
            plot_name=plot_name,
            args=mn_args,
        ))

    @triton.testing.perf_report(config)
    def benchmark(M, N, provider, model=None):
        mode = args.mode

        x = torch.randn(M, N, device='cuda', dtype=dtype)
        y = torch.zeros_like(x, device='cuda')
        rsigma = torch.empty((M, ), device='cuda', dtype=torch.float32)
        dx = torch.empty(M, N, device='cuda', dtype=dtype, requires_grad=False)
        dg = torch.empty((1, N), device='cuda', dtype=dtype, requires_grad=False)
        dg_tmp = torch.zeros(M, N, device='cuda', dtype=torch.float32, requires_grad=False)
        n_rows, n_cols = x.shape
        #        MAX_FUSED_SIZE = 65536 // x.element_size()
        #        blk_size = min(MAX_FUSED_SIZE, triton.next_power_of_2(n_cols))
        blk_size = 1024
        USE_BLOCKED = n_cols > blk_size
        NUM_PRGMS = min(n_rows, get_num_sms())
        stream = torch.cuda.Stream()
        torch.cuda.set_stream(stream)
        g = torch.ones((1, N), device='cuda')
        ZERO_CENTERED_GAMMA = False

        def rms_fwd():
            if provider == 'triton':
                return rmsnorm(x, g, y, rsigma, dx, dg, dg_tmp, n_rows, n_cols, ZERO_CENTERED_GAMMA, blk_size,
                               USE_BLOCKED, NUM_PRGMS)
            if provider == 'torch':
                return torch_rmsnorm_fwd(x, g, ZERO_CENTERED_GAMMA)

        if mode == 'fwd':
            ms = triton.testing.do_bench(rms_fwd)

        elif mode == 'bwd':
            x_ = x.clone().detach().requires_grad_()
            g_ = g.clone().detach().requires_grad_()
            # Preallocate
            y_ = torch.zeros_like(x_, dtype=dtype)
            rsigma_ = torch.empty((M, ), device='cuda', dtype=torch.float32)
            dx_ = torch.empty_like(x_, dtype=dtype)
            dg_tmp_ = torch.empty_like(x_, dtype=torch.float32)
            dg_ = torch.empty_like(g_, dtype=dtype)
            grad_out = torch.randn_like(y_)

            y_out = rmsnorm(x_, g_, y_, rsigma_, dx_, dg_, dg_tmp_, n_rows, n_cols, ZERO_CENTERED_GAMMA, blk_size,
                            USE_BLOCKED, NUM_PRGMS)

            ms = triton.testing.do_bench(lambda: y_out.backward(grad_out, retain_graph=True), grad_to_none=[x_, g_])
        else:
            raise ValueError(f"mode {mode} is not supported!")

        global verbose
        if verbose:
            print(f'SIZE: {N} Best tuning config: ({rms_kernel.best_config})')
            print(f'time: {ms}')
        gbps = lambda ms_val: 2 * x.nelement() * x.element_size() * 1e-9 / (ms_val * 1e-3)
        return gbps(ms)

    benchmark.run(save_path=".", show_plots=True, print_data=True)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Benchmark RMSNorm",
        allow_abbrev=False,
    )
    parser.add_argument('-model_configs', type=str, default="model_configs.json", help="Model config json file.")

    available_models = get_available_models(model_families=["llama3"])  # Dynamically load model names
    model_help = (
        "Model name to benchmark. Select from: [" + ", ".join(available_models) +
        "]. Use 'all' to benchmark all models. Not providing runs the default benchmark script with custom configs.")
    parser.add_argument('-model', type=str, default=None, help=model_help)
    parser.add_argument('-b', type=int, default=0, help="Batch size used together with model.")
    parser.add_argument('-sq', type=int, default=0, help="Sequence length used together with model.")
    parser.add_argument('-M', "--M_start", default="1", type=int)
    parser.add_argument('-Ms', "--M_step", default="2", type=int)  #This is multiplicative step
    parser.add_argument('-Me', "--M_end", default="512", type=int)
    parser.add_argument('-Mb', "--M_benchmark", default=False, type=bool)

    parser.add_argument('-N', "--N_start", default="8192", type=int)
    parser.add_argument('-Ns', "--N_step", default="1024", type=int)
    parser.add_argument('-Ne', "--N_end", default="32768", type=int)

    parser.add_argument('-d', "--dtype", default="fp16")
    parser.add_argument('-nb', "--no_benchmark", default=False, type=bool)
    parser.add_argument("-v", action='store_true', default=False, help="Print out the best tuning config")
    parser.add_argument("--mode", type=str, choices=["fwd", "bwd"], default="fwd",
                        help="Benchmark mode: forward only, backward only, or both.")

    return parser.parse_args()


def main():
    args = parse_args()
    global verbose
    if args.no_benchmark:
        x = torch.randn(args.M_start, args.N_start, device='cuda', dtype=args.dtype)
        y = torch.zeros_like(x, device='cuda')
        rsigma = torch.empty((args.M_start, ), device='cuda', dtype=torch.float32)
        dx = torch.empty(args.M_start, args.N_start, device='cuda', dtype=args.dtype, requires_grad=False)
        dg = torch.empty((1, args.N_start), device='cuda', dtype=args.dtype, requires_grad=False)
        dg_tmp = torch.zeros(args.M_start, args.N_start, device='cuda', dtype=torch.float32, requires_grad=False)
        n_rows, n_cols = x.shape
        MAX_FUSED_SIZE = 65536 // x.element_size()
        blk_size = min(MAX_FUSED_SIZE, triton.next_power_of_2(n_cols))
        USE_BLOCKED = n_cols > blk_size
        NUM_PRGMS = min(n_rows, get_num_sms())
        g = torch.ones((1, args.N_start), device='cuda', dtype=args.dtype)
        ZERO_CENTERED_GAMMA = True
        rmsnorm(x, y, g, rsigma, dx, dg, dg_tmp, n_rows, n_cols, ZERO_CENTERED_GAMMA, blk_size, USE_BLOCKED, NUM_PRGMS)
    else:
        verbose = args.v
        run_benchmark(args)


if __name__ == "__main__":
    sys.exit(main())

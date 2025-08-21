import triton
import triton.language as tl

configs = [
    triton.Config({"BLOCK_SIZE": 128}, num_warps=2, num_stages=2),
    triton.Config({"BLOCK_SIZE": 128}, num_warps=4, num_stages=3),
    triton.Config({"BLOCK_SIZE": 256}, num_warps=2, num_stages=2),
    triton.Config({"BLOCK_SIZE": 256}, num_warps=4, num_stages=3),
    triton.Config({"BLOCK_SIZE": 512}, num_warps=2, num_stages=2),
    triton.Config({"BLOCK_SIZE": 512}, num_warps=4, num_stages=3),
    triton.Config({"BLOCK_SIZE": 1024}, num_warps=2, num_stages=2),
    triton.Config({"BLOCK_SIZE": 1024}, num_warps=4, num_stages=4),
]


@triton.autotune(configs=configs, key=["total_elems"])
@triton.jit
def append_token_kernel(
    CUR_BLOCK_IDX,  # int32 pointer, shape [BS]
    TOKEN_PTR,  # float pointer, shape [BS, 1, D0, D1]
    CACHE_PTR,  # float pointer, shape [B, P, D0, D1]
    CACHE_POSITION,  # int32 pointer, shape [1] (tensor scalar)
    total_elems,
    stride_p,
    stride_cache_b,
    PAGE_SIZE: tl.constexpr,
    BLOCK_SIZE: tl.constexpr,
):
    """
    Modified: pos_in_block is now a tensor scalar.
    """
    pid = tl.program_id(axis=0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < total_elems
    b = offsets // stride_p
    rem = offsets % stride_p

    # Prepare page indexing
    block_idx = tl.load(CUR_BLOCK_IDX + b, mask=mask)
    cache_position = tl.load(CACHE_POSITION)
    position_in_page = cache_position % PAGE_SIZE
    cache_offset = block_idx * stride_cache_b + position_in_page * stride_p + rem

    # Load and store token
    token_offset = b * stride_p + rem
    val = tl.load(TOKEN_PTR + token_offset, mask=mask, other=0.0)
    tl.store(CACHE_PTR + cache_offset, val, mask=mask)

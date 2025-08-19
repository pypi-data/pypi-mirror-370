from b10_kernel.cute.rmsnorm import rmsnorm

__all__ = [
    "rmsnorm",
]

# Workaround for cutlass cache file issue: https://github.com/pytorch/pytorch/issues/156670
import cutlass
import os

if not hasattr(cutlass, "CACHE_FILE"):
    cutlass.CACHE_FILE = os.path.join(os.path.expanduser("~"), ".cutlass_cache")

import functools

import torch


def get_cuda_stream() -> int:
    return torch.cuda.current_stream().cuda_stream


@functools.lru_cache(maxsize=1)
def is_hopper_arch() -> bool:
    # Hopper arch's compute capability == 9.0
    device = torch.cuda.current_device()
    major, minor = torch.cuda.get_device_capability(device)
    return major == 9

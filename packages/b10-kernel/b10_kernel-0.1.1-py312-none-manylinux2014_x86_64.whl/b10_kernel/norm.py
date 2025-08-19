from typing import Optional

import torch
from b10_kernel.utils import is_hopper_arch


def rmsnorm(
    input_: torch.Tensor,
    weight: torch.Tensor,
    eps: float = 1e-6,
    out: Optional[torch.Tensor] = None,
    enable_pdl: Optional[bool] = None,
) -> torch.Tensor:
    r"""Root mean square normalization.

    ``out[i] = (input[i] / RMS(input)) * weight[i]``

    Parameters
    ----------
    input_: torch.Tensor
        Input tensor, shape (batch_size, hidden_size).
    weight: torch.Tensor
        Weight tensor, shape (hidden_size,).
    eps: float
        Epsilon for numerical stability.
    out: Optional[torch.Tensor]
        The output tensor, if specified, the kernel will update this tensor inplace.
    enable_pdl: Optional[bool]
        Whether to enable `programmatic dependent launch
        <https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#programmatic-dependent-launch-and-synchronization>`_
        If None, will be automatically enabled on Hopper architecture.

    Returns
    -------
    output: torch.Tensor
        Normalized tensor, shape (batch_size, hidden_size).
    """
    if out is None:
        out = torch.empty_like(input_)
    if enable_pdl is None:
        enable_pdl = is_hopper_arch()
    torch.ops.b10_kernel.rmsnorm.default(out, input_, weight, eps, enable_pdl)
    return out

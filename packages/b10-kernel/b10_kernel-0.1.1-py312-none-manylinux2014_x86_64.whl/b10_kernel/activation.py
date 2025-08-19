import torch


def silu_and_mul(
    input: torch.Tensor, output: torch.Tensor = None, is_reverse: bool = False
) -> torch.Tensor:
    """
    Silu and multiply the two parts of the input tensor.
    is_reverse:
    - If is_reverse is True, the first part of the input tensor is multiplied by the silu of the second part.
    - If is_reverse is False, the silu of the first part of the input tensor is multiplied by the second part.
    """
    if output is not None:
        assert input.ndim == output.ndim, f"{input.ndim} != {output.ndim}"
        assert input.shape[:-1] == output.shape[:-1], (
            f"{input.shape[:-1]} != {output.shape[:-1]}"
        )
        assert input.shape[-1] == 2 * output.shape[-1], (
            f"{input.shape[-1]} != {2 * output.shape[-1]}"
        )
    else:
        output = torch.empty(
            input.shape[:-1] + (input.shape[-1] // 2,),
            device=input.device,
            dtype=input.dtype,
        )
    torch.ops.b10_kernel.silu_and_mul.default(output, input, is_reverse)
    return output

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import torch

logger = logging.getLogger(__name__)


def clip_grad_norm_fsdp(
    parameters, process_group, max_norm, norm_type=2.0, error_if_nonfinite=False
):
    max_norm = float(max_norm)
    norm_type = float(norm_type)
    parameters = [p for p in parameters if p.grad is not None]
    if len(parameters) == 0:
        local_norm = torch.tensor(0.0).cuda()
    else:
        device = parameters[0].grad.device
        if norm_type == torch._six.inf:
            tmp_norms = [p.grad.detach().abs().max().to(device) for p in parameters]
            local_norm = (
                tmp_norms[0]
                if len(tmp_norms) == 1
                else torch.max(torch.stack(tmp_norms))
            )
        else:
            local_norm = torch.norm(
                torch.stack(
                    [
                        torch.norm(p.grad.detach(), norm_type).to(device)
                        for p in parameters
                    ]
                ),
                norm_type,
            )
        local_norm = local_norm.to(device)
    group_size = torch.distributed.get_world_size(group=process_group)
    gathered_norms = [torch.empty_like(local_norm) for _ in range(group_size)]
    torch.distributed.all_gather(gathered_norms, local_norm, group=process_group)
    if len(gathered_norms) == 0:
        return torch.tensor(0.0)
    if norm_type == torch._six.inf:
        total_norm = (
            gathered_norms[0]
            if len(gathered_norms) == 1
            else torch.max(torch.stack(gathered_norms))
        )
    else:
        total_norm = torch.norm(torch.stack(gathered_norms), norm_type)
    if total_norm.isnan() or total_norm.isinf():
        if error_if_nonfinite:
            error_msg = (
                f"The total norm of order {norm_type} for gradients from "
                "`parameters` is non-finite, so it cannot be clipped. To disable "
                "this error and scale the gradients by the non-finite norm anyway, "
                "set `error_if_nonfinite=False`"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        else:
            logger.warning(
                "Non-finite norm encountered in torch.nn.utils.clip_grad_norm_; continuing anyway. "
                "Note that the default behavior will change in a future release to error out "
                "if a non-finite total norm is encountered. At that point, setting "
                "error_if_nonfinite=false will be required to retain the old behavior."
            )
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1:
        for p in parameters:
            p.grad.detach().mul_(clip_coef.to(p.grad.device))
    logger.debug(f"total norm: {total_norm}")
    return total_norm

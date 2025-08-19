# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import OrderedDict
import copy
import logging
from mpi4py import MPI
import torch
import torch.nn as nn
import torch.distributed.distributed_c10d as dist_c10d
from torch._utils import _flatten_dense_tensors, _unflatten_dense_tensors

logger = logging.getLogger(__name__)


def monkey_patch_apex_amp_scaler():
    from apex import amp

    def update_scale(self):
        # If the fused kernel is available, we only need one D2H memcopy and sync.
        if self.has_fused_kernel and self.dynamic and not self._has_overflow:
            self._has_overflow = self._overflow_buf.item()

        # Adding syncing of self._has_overflow across all processes
        if torch.distributed.is_initialized():
            if MPI.COMM_WORLD.Get_size() == torch.distributed.get_world_size():
                self._has_overflow = MPI.COMM_WORLD.allreduce(
                    self._has_overflow, MPI.MAX
                )
            else:
                tmp_has_overflow = torch.tensor(self._has_overflow).to(
                    torch.cuda.current_device()
                )
                torch.distributed.all_reduce(
                    tmp_has_overflow, op=torch.distributed.ReduceOp.MAX
                )
                self._has_overflow = tmp_has_overflow.item()

        if self._has_overflow and self.dynamic:
            should_skip = True
            if self._min_loss_scale:
                self._loss_scale = max(self._min_loss_scale, self._loss_scale / 2.0)
            else:
                self._loss_scale = self._loss_scale / 2.0
            self._unskipped = 0
        else:
            should_skip = False
            self._unskipped += 1

        if self._unskipped == self._scale_seq_len and self.dynamic:
            self._loss_scale = min(self._max_loss_scale, self._loss_scale * 2.0)
            self._unskipped = 0

        return should_skip

    amp.scaler.LossScaler.update_scale = update_scale


class DistributedModelDataParallel(nn.Module):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.process_groups = self.module.process_groups

        # check all the processes should have same dist_grids for the model
        all_dist_grids = MPI.COMM_WORLD.allgather(self.module.dist_grids)
        logger.debug(f"all_dist_grids: {all_dist_grids}")
        assert (
            len(set([len(tmp_dgrid) for tmp_dgrid in all_dist_grids])) == 1
        ), f"All processes should have same list of dist_grids for same model. {all_dist_grids}"
        for tmp_dgrid in zip(*all_dist_grids):
            assert (
                len(set(tmp_dgrid)) == 1
            ), f"All processes should have same list of dist_grids for same model. {all_dist_grids}"

        self.dgrid_state_dict_keys = OrderedDict()
        for dgrid in self.module.dist_grids:
            self.dgrid_state_dict_keys[dgrid] = []
        for k in self.module.state_dict().keys():
            dp_group_name, mp_group_name = self.module.state_dict_to_dist_grid(k)
            self.dgrid_state_dict_keys[(dp_group_name, mp_group_name)].append(k)

        self.dgrid_named_params = OrderedDict()
        for dgrid in self.module.dist_grids:
            self.dgrid_named_params[dgrid] = []
        for name, param in self.module.named_parameters():
            dp_group_name, mp_group_name = self.module.named_param_to_dist_grid(
                name, param
            )
            self.dgrid_named_params[(dp_group_name, mp_group_name)].append(
                (name, param)
            )

        logger.debug(f"self.dgrid_state_dict_keys: {self.dgrid_state_dict_keys}")
        logger.debug(
            f"""self.dgrid_named_params:
            {dict((k, [(n, p.size()) for n, p in v]) for k, v in self.dgrid_named_params.items())}"""
        )
        self.broadcast_params()

    def forward(self, *inputs, **kwargs):
        return self.module(*inputs, **kwargs)

    def state_dict(self, destination=None, prefix="", keep_vars=False):
        return self.module.state_dict(destination, prefix, keep_vars)

    def load_state_dict(self, state_dict, strict=True):
        self.module.load_state_dict(state_dict, strict=strict)

    def get_world_size(self, group_name):
        return self.module.get_world_size(group_name)

    def get_rank(self, group_name):
        return self.module.get_rank(group_name)

    def group_state_dict_by_dgrid(self, state_dict):
        dgrid_state_dict = OrderedDict()
        for dgrid, state_dict_keys in self.dgrid_state_dict_keys.items():
            dgrid_state_dict[dgrid] = OrderedDict(
                (key, state_dict[key]) for key in state_dict_keys
            )
        return dgrid_state_dict

    def _group_params_by_dgrid_and_dtype(self):
        groups = OrderedDict()
        for (
            dp_group_name,
            mp_group_name,
        ), named_params in self.dgrid_named_params.items():
            for _, param in named_params:
                group_key = (dp_group_name, mp_group_name, param.dtype)
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(param)
        # logger.debug(f"params grouped by dgrid and dtype:
        # {dict((k, [p.size() for p in v]) for k, v in groups.items())}")
        return groups

    def broadcast_params(self, numel_per_bucket=500000000):
        def bucket_broadcast_and_copy(datas_bucket, broadcast_src_rank, process_group):
            assert process_group is not None
            coalesced = _flatten_dense_tensors(datas_bucket)
            torch.distributed.broadcast(
                coalesced, broadcast_src_rank, group=process_group
            )
            torch.cuda.synchronize()
            synced = _unflatten_dense_tensors(coalesced, datas_bucket)
            for d, s in zip(datas_bucket, synced):
                d.copy_(s)

        groups = self._group_params_by_dgrid_and_dtype()
        for (dp_group_name, _, _), group in groups.items():
            process_group = self.process_groups[dp_group_name]
            if process_group is None:
                continue
            if process_group is dist_c10d._get_default_group():
                broadcast_src_rank = 0
            else:
                broadcast_src_rank = dist_c10d._get_global_rank(process_group, 0)
            datas = [param.data for param in group]
            small_bucket = []
            numel = 0
            for tensor in datas:
                small_bucket.append(tensor)
                numel = numel + tensor.numel()
                if numel > numel_per_bucket:
                    bucket_broadcast_and_copy(
                        small_bucket, broadcast_src_rank, process_group
                    )
                    small_bucket = []
                    numel = 0
            if len(small_bucket) > 0:
                bucket_broadcast_and_copy(
                    small_bucket, broadcast_src_rank, process_group
                )

    def _get_gradient_predivide_factor(self, predivide_mode, world_size):
        assert predivide_mode in ["sqrt", "world_size", "1"]
        if predivide_mode == "sqrt":
            factor = 1
            while world_size % factor == 0 and world_size / factor > factor:
                factor *= 2
        elif predivide_mode == "world_size":
            factor = world_size
        else:  # predivide_mode == '1'
            factor = 1
        return float(factor)

    def all_reduce_grads(
        self,
        fp32_allreduce=False,
        no_scale=False,
        predivide_mode="sqrt",
        numel_per_bucket=500000000,
    ):
        def bucket_all_reduce_and_copy(
            grads_bucket, dtype, predivide_factor, postdivide_factor, process_group
        ):
            assert process_group is not None
            coalesced = _flatten_dense_tensors(grads_bucket)
            if fp32_allreduce and dtype != torch.float32:
                coalesced = coalesced.float()
            if not no_scale and predivide_factor != 1:
                coalesced.div_(predivide_factor)
            torch.distributed.all_reduce(
                coalesced, op=torch.distributed.ReduceOp.SUM, group=process_group
            )
            torch.cuda.synchronize()
            if not no_scale and postdivide_factor != 1:
                coalesced.div_(postdivide_factor)
            synced = _unflatten_dense_tensors(coalesced, grads_bucket)
            for g, s in zip(grads_bucket, synced):
                g.copy_(s)

        groups = self._group_params_by_dgrid_and_dtype()
        for (dp_group_name, _, dtype), group in groups.items():
            process_group = self.process_groups[dp_group_name]
            if process_group is None:
                continue
            world_size = torch.distributed.get_world_size(group=process_group)
            predivide_factor = self._get_gradient_predivide_factor(
                predivide_mode, world_size
            )
            postdivide_factor = world_size / predivide_factor
            for param in group:
                if param.requires_grad and param.grad is None:
                    # In cases where there is an imbalance of empty grads across
                    # ranks we must create zero grads, this will ensure that every
                    # rank is reducing the same size. In some cases it may make
                    # sense in the future to support the ability to average not
                    # w.r.t. world size but with a different value.
                    param.grad = torch.zeros(
                        param.size(), dtype=param.dtype, device=param.device
                    )
            grads = [param.grad.data for param in group if param.requires_grad]
            small_bucket = []
            numel = 0
            for tensor in grads:
                small_bucket.append(tensor)
                numel = numel + tensor.numel()
                if numel > numel_per_bucket:
                    bucket_all_reduce_and_copy(
                        small_bucket,
                        dtype,
                        predivide_factor,
                        postdivide_factor,
                        process_group,
                    )
                    small_bucket = []
                    numel = 0
            if len(small_bucket) > 0:
                bucket_all_reduce_and_copy(
                    small_bucket,
                    dtype,
                    predivide_factor,
                    postdivide_factor,
                    process_group,
                )

    @staticmethod
    def clip_grad_norm_(
        dgrid_params, process_groups, max_norm, norm_type=2.0, error_if_nonfinite=False
    ):
        max_norm = float(max_norm)
        norm_type = float(norm_type)
        norms = []
        for (_, mp_group_name), parameters in dgrid_params.items():
            parameters = [p for p in parameters if p.grad is not None]
            if len(parameters) == 0:
                local_norm = torch.tensor(0.0).cuda()
            else:
                device = parameters[0].grad.device
                if norm_type == torch._six.inf:
                    tmp_norms = [
                        p.grad.detach().abs().max().to(device) for p in parameters
                    ]
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
            if process_groups[mp_group_name] is None:
                norms.append(local_norm)
                logger.debug(f"local norm: {local_norm}")
            else:
                mp_group = process_groups[mp_group_name]
                mp_size = torch.distributed.get_world_size(group=mp_group)
                gathered_norms = [torch.empty_like(local_norm) for _ in range(mp_size)]
                torch.distributed.all_gather(gathered_norms, local_norm, group=mp_group)
                norms.extend(gathered_norms)
                logger.debug(
                    f"gathered norms for mp group {mp_group_name}: {gathered_norms}"
                )
        if len(norms) == 0:
            return torch.tensor(0.0)
        if norm_type == torch._six.inf:
            total_norm = norms[0] if len(norms) == 1 else torch.max(torch.stack(norms))
        else:
            total_norm = torch.norm(torch.stack(norms), norm_type)
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
            for _, parameters in dgrid_params.items():
                for p in parameters:
                    if p.grad is not None:
                        p.grad.detach().mul_(clip_coef.to(p.grad.device))
        logger.debug(f"total norm: {total_norm}")
        return total_norm


class ModelParallelOptimizer(object):
    def __init__(
        self, raw_model_parallel_module, optimizer_class, optimizer_parameters
    ):
        dgrid_param_groups = self._get_model_training_dgrid_param_groups(
            raw_model_parallel_module
        )

        self.dgrid_optimizer = OrderedDict()
        for dgrid in raw_model_parallel_module.dist_grids:
            self.dgrid_optimizer[dgrid] = optimizer_class(
                dgrid_param_groups[dgrid], **optimizer_parameters
            )

    def _get_model_training_dgrid_param_groups(self, raw_model_parallel_module):
        params = raw_model_parallel_module.get_training_parameters()
        if isinstance(params, torch.Tensor):
            raise TypeError(
                "params given to the optimizer should be an iterable of Tensors or dicts, but got "
                + torch.typename(params)
            )
        param_groups = list(params)
        if len(param_groups) == 0:
            raise ValueError("optimizer got an empty parameter list")
        if not isinstance(param_groups[0], dict):
            param_groups = [{"params": param_groups}]

        for param_group in param_groups:
            params = param_group["params"]
            if isinstance(params, torch.Tensor):
                param_group["params"] = [params]
            elif isinstance(params, set):
                raise TypeError(
                    "optimizer parameters need to be organized in ordered collections, but "
                    "the ordering of tensors in sets will change between runs. Please use a list instead."
                )
            else:
                param_group["params"] = list(params)

        empty_param_groups = []
        for param_group in param_groups:
            empty_param_group = {k: v for k, v in param_group.items() if k != "params"}
            empty_param_group["params"] = []
            empty_param_groups.append(empty_param_group)

        dgrid_param_groups = OrderedDict()
        for dgrid in raw_model_parallel_module.dist_grids:
            dgrid_param_groups[dgrid] = copy.deepcopy(empty_param_groups)
        for name, param in raw_model_parallel_module.named_parameters():
            found_in_param_groups = False
            for i, param_group in enumerate(param_groups):
                if param in set(param_group["params"]):
                    assert (
                        not found_in_param_groups
                    ), "Found same param in more than one param groups."
                    dp_group_name, mp_group_name = (
                        raw_model_parallel_module.named_param_to_dist_grid(name, param)
                    )
                    dgrid_param_groups[(dp_group_name, mp_group_name)][i][
                        "params"
                    ].append(param)
                    found_in_param_groups = True
            if not found_in_param_groups:
                logger.warning(f"Parameter {name} is not being optimized.")
        for dgrid in raw_model_parallel_module.dist_grids:
            dgrid_param_groups[dgrid] = [
                tmp_param_group
                for tmp_param_group in dgrid_param_groups[dgrid]
                if len(tmp_param_group["params"]) > 0
            ]

        logger.debug("******************************************************")
        print_dict = {}
        for dgrid in raw_model_parallel_module.dist_grids:
            print_dict[dgrid] = []
            for param_group in dgrid_param_groups[dgrid]:
                print_dict[dgrid].append(
                    {k: v for k, v in param_group.items() if k != "params"}
                )
                print_dict[dgrid][-1]["param_sizes"] = [
                    p.size() for p in param_group["params"]
                ]
        logger.debug(f"dgrid_param_groups: {print_dict}")
        logger.debug("******************************************************")

        return dgrid_param_groups

    def zero_grad(self, *args, **kwargs):
        for optimizer in self.dgrid_optimizer.values():
            optimizer.zero_grad(*args, **kwargs)

    def step(self, *args, **kwargs):
        for optimizer in self.dgrid_optimizer.values():
            optimizer.step(*args, **kwargs)

    @property
    def inner_optimizer_list(self):
        return list(self.dgrid_optimizer.values())

    @inner_optimizer_list.setter
    def inner_optimizer_list(self, optimizer_list):
        assert len(optimizer_list) == len(self.dgrid_optimizer.keys())
        for dgrid, optimizer in zip(self.dgrid_optimizer.keys(), optimizer_list):
            self.dgrid_optimizer[dgrid] = optimizer

    def get_dgrid_state_dict(self):
        dgrid_state_dict = OrderedDict()
        for dgrid, optimizer in self.dgrid_optimizer.items():
            dgrid_state_dict[dgrid] = optimizer.state_dict()
        return dgrid_state_dict

    def load_dgrid_state_dict(self, dgrid_state_dict):
        for dgrid, optimizer in self.dgrid_optimizer.items():
            optimizer.load_state_dict(dgrid_state_dict[dgrid])


class ModelParallelLRScheduler(object):
    def __init__(
        self, model_parallel_optimizer, lr_scheduler_class, lr_scheduler_parameters
    ):
        self.dgrid_lr_scheduler = OrderedDict()
        for dgrid, optimizer in model_parallel_optimizer.dgrid_optimizer.items():
            self.dgrid_lr_scheduler[dgrid] = lr_scheduler_class(
                optimizer, **lr_scheduler_parameters
            )

    def get_last_lr(self):
        lr_scheduler = next(iter(self.dgrid_lr_scheduler.values()))
        if getattr(lr_scheduler, "get_last_lr", None) is not None:
            return lr_scheduler.get_last_lr()
        else:
            return lr_scheduler.get_lr()

    def step(self, *args, **kwargs):
        for lr_scheduler in self.dgrid_lr_scheduler.values():
            lr_scheduler.step(*args, **kwargs)

    def get_dgrid_state_dict(self):
        dgrid_state_dict = OrderedDict()
        for dgrid, lr_scheduler in self.dgrid_lr_scheduler.items():
            dgrid_state_dict[dgrid] = lr_scheduler.state_dict()
        return dgrid_state_dict

    def load_dgrid_state_dict(self, dgrid_state_dict):
        for dgrid, lr_scheduler in self.dgrid_lr_scheduler.items():
            lr_scheduler.load_state_dict(dgrid_state_dict[dgrid])

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import re
import os

import torch
import torch.nn as nn

from azureml.acft.image.components.mainztrain.Models.Networks.GenericTorchModel import GenericTorchModel
from ..Utils import NORM_MODULES
from ..Utils import is_main_process
from ..Utils import DistributionGridFactory
from ..Utils import analysis_model


logger = logging.getLogger(__name__)


def _is_depthwise(m):
    return (
        isinstance(m, nn.Conv2d)
        and m.groups == m.in_channels
        and m.groups == m.out_channels
    )


_model_wrappers = {}


def register_model_wrapper(module):
    _model_wrappers[module.__name__] = module
    return module


def model_wrappers(model_name):
    return _model_wrappers[model_name]


@register_model_wrapper
class GenericModel(GenericTorchModel):
    """
    A wrapper model for interfacing pytorch vision models with MainzTrainer
    We can not set seperated weight decay in MainzTrainer,
    and add weight decay setting function in VisionModel
    """

    def __init__(self, opt, module: nn.Module):
        """
        Args:
            opt (dict): configuration dict provided by MainzTrainer
            module (nn.Module): pytorch model to be wrapped
        """
        super(GenericModel, self).__init__(opt, module)

    def customize_params(self, customized_params_conf, base_lr, weight_decay):
        no_decay_module_names = customized_params_conf.get(
            "NO_WEIGHT_DECAY_MODULES", []
        )
        no_decay_params = []

        for m in self.model.modules():
            if "dw" in no_decay_module_names and _is_depthwise(m):
                no_decay_params.append(m.weight)
            elif "norm" in no_decay_module_names and isinstance(m, tuple(NORM_MODULES)):
                no_decay_params.append(m.weight)
                no_decay_params.append(m.bias)

        param_group_names = {}
        param_group_vars = {}

        weight_decay_patterns = customized_params_conf.get("WEIGHT_DECAY_PATTERNS", {})
        lr_scale_patterns = customized_params_conf.get("LR_SCALE_PATTERNS", {})

        for name, param in self.model.named_parameters():
            for freeze_pattern in customized_params_conf.get("FREEZE_PATTERNS", []):
                if re.search(freeze_pattern, name):
                    param.requires_grad = False
                    break

            if not param.requires_grad:
                continue

            current_lr = base_lr
            current_weight_decay = weight_decay

            weight_decay_set = False
            for p in no_decay_params:
                if p is param:
                    current_weight_decay = 0.0
                    weight_decay_set = True

            for pattern, value in weight_decay_patterns.items():
                if weight_decay_set:
                    break
                if re.search(pattern, name):
                    current_weight_decay = value
                    weight_decay_set = True
                    break

            for pattern, value in lr_scale_patterns.items():
                if re.search(pattern, name):
                    current_lr = base_lr * value
                    break

            group_name = (
                f"weight_decay: {current_weight_decay:.7f}, lr: {current_lr:.7f}"
            )
            if group_name not in param_group_names:
                param_group_names[group_name] = {
                    "weight_decay": current_weight_decay,
                    "params": [],
                    "lr": current_lr,
                }
                param_group_vars[group_name] = {
                    "weight_decay": current_weight_decay,
                    "params": [],
                    "lr": current_lr,
                }

            param_group_names[group_name]["params"].append(name)
            param_group_vars[group_name]["params"].append(param)

        if is_main_process():
            logger.info(
                "Param groups = {}".format(json.dumps(param_group_names, indent=2))
            )
            param_group_sizes = {
                k: len(v["params"]) for k, v in param_group_names.items()
            }
            logger.info(
                "Param group sizes: {}".format(json.dumps(param_group_sizes, indent=2))
            )

        return list(param_group_vars.values())

    def filter_wd(self):
        "filter_wd is deprecated, please use customize_params()"
        without_decay_list = self.opt["TRAIN"]["WITHOUT_WD_LIST"]
        without_decay_depthwise = []
        without_decay_norm = []
        for m in self.model.modules():
            if _is_depthwise(m) and "dw" in without_decay_list:
                without_decay_depthwise.append(m.weight)
            elif isinstance(m, nn.BatchNorm2d) and "bn" in without_decay_list:
                without_decay_norm.append(m.weight)
                without_decay_norm.append(m.bias)
            elif isinstance(m, nn.GroupNorm) and "gn" in without_decay_list:
                without_decay_norm.append(m.weight)
                without_decay_norm.append(m.bias)
            elif isinstance(m, nn.LayerNorm) and "ln" in without_decay_list:
                without_decay_norm.append(m.weight)
                without_decay_norm.append(m.bias)

        with_decay = []
        without_decay = []

        skip = {}
        if hasattr(self.model, "no_weight_decay"):
            skip = self.model.no_weight_decay()

        skip_keys = {}
        if hasattr(self.model, "no_weight_decay_keywords"):
            skip_keys = self.model.no_weight_decay_keywords()

        for n, p in self.model.named_parameters():
            ever_set = False

            if p.requires_grad is False:
                continue

            skip_flag = False
            if n in skip:
                logger.info(f"set {n} wd to 0")
                without_decay.append(p)
                skip_flag = True
            else:
                for i in skip:
                    if i in n:
                        logger.info(f"set {n} wd to 0")
                        without_decay.append(p)
                        skip_flag = True

            if skip_flag:
                continue

            for i in skip_keys:
                if i in n:
                    logger.info(f"set {n} wd to 0")

            if skip_flag:
                continue

            for pp in without_decay_depthwise:
                if p is pp:
                    if self.opt["VERBOSE"]:
                        logger.info(f"set depthwise({n}) wd to 0")
                    without_decay.append(p)
                    ever_set = True
                    break

            for pp in without_decay_norm:
                if p is pp:
                    if self.opt["VERBOSE"]:
                        logger.info(f"set norm({n}) wd to 0")
                    without_decay.append(p)
                    ever_set = True
                    break

            if (not ever_set) and "bias" in without_decay_list and n.endswith(".bias"):
                if self.opt["VERBOSE"]:
                    logger.info(f"set bias({n}) wd to 0")
                without_decay.append(p)
            elif not ever_set:
                with_decay.append(p)

        # assert (len(with_decay) + len(without_decay) == len(list(model.parameters())))
        params = [
            {"params": with_decay},
            {"params": without_decay, "weight_decay": 0.0},
        ]
        return params

    def get_training_parameters(self):
        """
        Return model parameters or grouped parameters to be optimized
        """

        params = []
        if "CUSTOMIZED_PARAMS_CONF" in self.opt:
            base_lr = self.opt["START_LEARNING_RATE"]
            weight_decay = self.opt["OPTIMIZER_PARAMS"].get("weight_decay", 0)
            params = self.customize_params(
                self.opt["CUSTOMIZED_PARAMS_CONF"], base_lr, weight_decay
            )
        elif "CUSTOMIZED_PARAMS_FUNC" in self.opt:
            params = getattr(self.model, self.opt["CUSTOMIZED_PARAMS_FUNC"]["NAME"])(
                self.opt
            )
        else:
            params = [p for p in self.parameters() if p.requires_grad]

        return params

    def analysis_model(self, submodule_str, dump_input, verbose):
        module = self.get_submodule(submodule_str)
        analysis_model(module, dump_input, verbose)

    def get_loss_info(self, loss):
        loss_info = {"train_loss": loss.detach().item()}
        return loss, loss_info

    def get_submodule(self, prefix):
        res = self
        keys = prefix.split(".")
        for key in keys:
            if key:
                res = getattr(res, key)
        return res


@register_model_wrapper
class MoEModel(GenericModel):
    def __init__(self, opt, module: nn.Module):
        """
        A wrapper model for interfacing moe vision models with MainzTrainer
        Inherit the weight and lr modifications from GenericModel
        """
        super().__init__(opt, module)

        assert "MOE" in self.opt, "MoEModel is only used for wrapping moe models"
        logger.info("Init a MoE vision model")
        assert self.opt["DDP"] in ["MAINZ", "OSS"], "Only support Mainz and OSS DDP"
        for group_name, group in self.opt["MOE"].items():
            expert_parallel_size = group["ORT_EXPERT_PARALLEL_SIZE"]
            expert_replica_size = self.opt["world_size"] // expert_parallel_size
            distributed_group = DistributionGridFactory.get_distribution_grid(
                expert_parallel_size, expert_replica_size, self.opt["DDP"]
            )
            self.process_groups[f"{group_name}_expert_dp_group"] = (
                distributed_group.get_expert_replica_group()
            )
            self.process_groups[f"{group_name}_expert_mp_group"] = (
                distributed_group.get_expert_parallel_group()
            )

        # TODO: add init from pretrained
        # init from pretrained, old API
        # if self.opt.get('PYLEARN_MODEL', '') != '':
        #     logger.warning("Use old VisionModel API to init from pretrained MoE CLIP")
        #     # DATA_DIR + PYLEARN_MODEL + default
        #     self.from_pretrained(os.path.join(self.opt['PYLEARN_MODEL'], "default"))

    def state_dict_to_dist_grid(self, state_dict_key):
        from ort_moe.utils import _expert_state_dict_keyword

        for group_name, group in self.opt["MOE"].items():
            if (
                _expert_state_dict_keyword in state_dict_key
                and state_dict_key.startswith(group["PREFIX"])
            ):
                # is expert param and is in one of the groups
                return (
                    f"{group_name}_expert_dp_group",
                    f"{group_name}_expert_mp_group",
                )
        return ("world", "")

    def named_param_to_dist_grid(self, param_name, param):
        from ort_moe.utils import _expert_state_dict_keyword

        for group_name, group in self.opt["MOE"].items():
            if _expert_state_dict_keyword in param_name and param_name.startswith(
                group["PREFIX"]
            ):
                # is expert param and is in one of the groups
                return (
                    f"{group_name}_expert_dp_group",
                    f"{group_name}_expert_mp_group",
                )
        return ("world", "")

    def analysis_model(self, submodule_str, dump_input, verbose):
        moe_groups = {
            v["PREFIX"]: v["ORT_EXPERT_PARALLEL_SIZE"]
            for k, v in self.opt["MOE"].items()
        }

        total_model_size = 0
        single_gpu_model_size = 0
        for n, p in self.named_parameters():
            if not p.requires_grad:
                continue
            if not n.startswith(submodule_str):
                continue
            if hasattr(p, "is_moe_param") and p.is_moe_param:  # is moe param
                multiplier = -1
                for group, v in moe_groups.items():
                    group_wo_prefix = group[6:]  # remove "model." in the prefix
                    if group_wo_prefix or n.startswith(group):
                        multiplier = v
                assert multiplier != -1, "each moe param needs to be in a moe group"
                total_model_size += p.numel() * multiplier
                single_gpu_model_size += p.numel()
            else:  # non-moe param
                total_model_size += p.numel()
                single_gpu_model_size += p.numel()

        logger.info(f"  Total params: {total_model_size/1000/1000:.3f}M")
        logger.info(f"  Single GPU params: {single_gpu_model_size/1000/1000:.3f}M")
        return

    def get_loss_info(self, loss):
        loss_info = {"train_loss": loss.detach().item()}

        from ort_moe.utils import get_moe_loss

        # MoE Loss
        for group_name, group in self.opt["MOE"].items():
            moe_loss, gate_log, num_moe_layers = get_moe_loss(
                self.get_submodule(group["PREFIX"]), False, dtype=loss.dtype
            )

            if self.opt.get("SCALE_MOE_LOSS", False):
                # the model loss is normalized using the effective batch size after gathering from all mini-batches
                # so the model gradients are (world_size * grad_accu_step) times smaller than their real values
                # instead of rescaling the model gradients, we reverse-scaling the moe gradients here to prevent
                # potential impact to other hyper-parameters
                # default GATHERED_LOSS_NORM is True
                moe_loss /= (
                    self.opt["world_size"] * self.opt["GRADIENT_ACCUMULATE_STEP"]
                )
                loss += moe_loss
            # moe loss logs
            for key, val in gate_log.items():
                if val.ndim == 0:
                    loss_info[f"{group_name}_{key}"] = val.detach().item()
                else:
                    for i in range(len(val)):
                        loss_info[f"{group_name}_{key}_e{i}"] = val[i].detach().item()
                    val = sorted(val.detach().tolist())
                    for i in range(len(val)):
                        loss_info[f"{group_name}_{key}_sorted_e{i}"] = val[i]

        return loss, loss_info

    def merge_moe_state_dict(self, moe_dicts):

        def intTryParse(value):
            try:
                return int(value)
            except ValueError:
                return -1

        def get_moe_expert_index(k):
            random_key = k.split(".")
            indicator = random_key[random_key.index("moe_experts") + 1]
            return intTryParse(indicator)

        result = {}
        # get a key from state dict and check whether moe_experts.{0} is in the key
        random_key = list(moe_dicts[0])[0]
        is_merged_ffn = False if get_moe_expert_index(random_key) > -1 else True
        if is_merged_ffn:
            for key in moe_dicts[0].keys():
                weights = [weight_dict[key] for weight_dict in moe_dicts]
                weight_merged = torch.cat(weights)
                result[key] = weight_merged
        else:
            N_local_experts = -1
            for k, v in moe_dicts[0].items():
                N_local_experts = max(get_moe_expert_index(k), N_local_experts)
            N_local_experts += 1
            for dict_index, moe_dict in enumerate(moe_dicts):
                for k, v in moe_dict.items():
                    expert_index = get_moe_expert_index(k)
                    result[
                        k.replace(
                            "moe_experts.{expert_index}",
                            f"moe_experts.{expert_index + N_local_experts * dict_index}",
                        )
                    ] = v

        return result

    def from_pretrained(self, load_dir):
        # load_dir for eval is: DATA_DIR + PYLEARN_MODEL + default
        # old API
        # load_checkpoint =self.opt.get("LOAD_CHECKPOINT", False)
        # if load_checkpoint:
        if os.path.exists(os.path.join(load_dir, "module_training_states.pt")):
            logger.info("Load from checkpoints")
            # compatable for old saving format or do not save pretrained
            # assumption: local num experts = 1 in the training, thus rank 0 - num experts are useful
            # we have ORT_PARALLEL GPUs (G) for num experts (E), for each rank, we have E // G experts
            # thus for rank i, we should load [i * E//G, (i+1)*E//G)
            pretrained_dict = torch.load(
                os.path.join(load_dir, "module_training_states__rank_0.pt"),
                map_location="cpu",
            )["module"]

            for group_name, group in self.opt["MOE"].items():
                G_old = len(
                    [
                        dir
                        for dir in os.listdir(load_dir)
                        if f"module_training_states_{group_name}_expert_mp_group_rank"
                        in dir
                    ]
                )
                G = group["ORT_EXPERT_PARALLEL_SIZE"]
                assert (
                    G_old >= G
                ), "In pure evaluation, we always use small number of GPUs"
                # moe_type = None
                # moe_type_dict =  [torch.load(os.path.join(load_dir,
                # f"module_training_states_vision_expert_mp_group_rank_{eval_rank * num_merge_ranks + rank}.pt"),
                # map_location='cpu')['module'] for rank in range(num_merge_ranks)]
                num_merge_ranks = G_old // G
                eval_rank = self.opt["rank"]
                moe_dicts = [
                    torch.load(
                        os.path.join(
                            load_dir,
                            f"""module_training_states_{group_name}_expert_mp_group_rank_
                            {eval_rank * num_merge_ranks + rank}.pt""",
                        ),
                        map_location="cpu",
                    )["module"]
                    for rank in range(num_merge_ranks)
                ]
                moe_dict = self.merge_moe_state_dict(moe_dicts)
                pretrained_dict.update(moe_dict)

            pretrained_dict = {k[6:]: v for k, v in pretrained_dict.items()}
            missing_keys, unexpected_keys = self.model.load_state_dict(pretrained_dict)
            if missing_keys:
                logger.info(f"missing keys: {missing_keys}")
            if unexpected_keys:
                logger.info(f"unexpected_keys: {unexpected_keys}")
            # self.model.from_pretrained(pretrained_dict)
            return self
        else:
            # traditional loading
            load_path = os.path.join(
                load_dir, self.opt.get("PYLEARN_MODEL_FILE_NAME", "model_state_dict.pt")
            )
            state_dict = torch.load(load_path, map_location=self.opt["device"])
            self.model.load_state_dict(state_dict)
            return self

    def save_pretrained(self, save_dir):
        return save_dir

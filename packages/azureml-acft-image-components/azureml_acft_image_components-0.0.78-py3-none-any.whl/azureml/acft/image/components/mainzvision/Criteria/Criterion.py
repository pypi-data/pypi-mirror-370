# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import torch as th
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint
from torch.distributed.nn import all_gather as differentiable_all_gather
# from torch.distributed.nn import all_reduce as differentiable_all_reduce

import numpy as np
import math


def linear_combination(x, y, epsilon):
    return epsilon * x + (1 - epsilon) * y


def reduce_loss(loss, reduction="mean"):
    return (
        loss.mean()
        if reduction == "mean"
        else loss.sum() if reduction == "sum" else loss
    )


class LabelSmoothingCrossEntropy(nn.Module):
    def __init__(self, epsilon=0.1, reduction="mean"):
        super().__init__()
        self.epsilon = epsilon
        self.reduction = reduction

    def forward(self, preds, target):
        n = preds.size()[-1]
        log_preds = F.log_softmax(preds, dim=-1)
        loss = reduce_loss(-log_preds.sum(dim=-1), self.reduction)
        nll = F.nll_loss(log_preds, target, reduction=self.reduction)
        return linear_combination(loss / n, nll, self.epsilon)


class FocalLoss(nn.Module):
    """
    Origianl code is from https://github.com/richardaecn/class-balanced-loss/blob/master/src/cifar_main.py#L226-L266
    """

    def __init__(self, alpha, gamma, normalize):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.normalize = normalize

    def forward(self, preds, targets):
        cross_entropy = F.binary_cross_entropy_with_logits(
            preds, targets, reduction="none"
        )

        gamma = self.gamma
        if gamma == 0.0:
            modulator = 1.0
        else:
            modulator = th.exp(
                -gamma * targets * preds - gamma * th.log1p(th.exp(-1.0 * preds))
            )

        loss = modulator * cross_entropy
        weighted_loss = self.alpha * loss
        focal_loss = reduce_loss(weighted_loss, reduction="sum")

        return focal_loss / targets.sum() if self.normalize else focal_loss


class MultiSoftmaxCrossEntropyLoss(nn.Module):
    def __init__(self, class_weight=None, label_smoothing_value=0):
        super(MultiSoftmaxCrossEntropyLoss, self).__init__()

        self.class_weight = class_weight
        if self.class_weight is not None:
            self.class_weight = self.class_weight.cuda()

        self.logsoftmax = nn.LogSoftmax(dim=1)
        self.label_smoothing_value = label_smoothing_value

    def forward(self, input, target):
        return self.cross_entropy(input, target, self.class_weight)

    def cross_entropy(self, pred, soft_targets, class_weight=None):
        if class_weight is not None:
            class_weight_matrix = class_weight.expand_as(soft_targets)
            used_class_weights = th.where(
                soft_targets > 0, class_weight_matrix, soft_targets
            )
            samples_weight = th.max(used_class_weights, dim=1, keepdim=True)[0]

            loss = th.mean(
                th.sum(-samples_weight * soft_targets * self.logsoftmax(pred), 1), 0
            )
        else:
            if self.label_smoothing_value > 0:
                # label smoothing
                batch_size, total_classes_count = soft_targets.size()
                for sample_index in range(batch_size):
                    pos_indices = np.where(soft_targets[sample_index, :] > 0)
                    pos_classes_count = len(pos_indices[0])
                    if pos_classes_count > 0:
                        neg_p = self.label_smoothing_value / float(
                            total_classes_count - pos_classes_count
                        )
                        pos_p = self.label_smoothing_value / pos_classes_count
                        soft_targets[sample_index, :] += neg_p
                        soft_targets[sample_index, pos_indices[0]] = (
                            soft_targets[sample_index, pos_indices[0]] - pos_p - neg_p
                        )

            loss = th.sum(-soft_targets * self.logsoftmax(pred))
            loss = loss / soft_targets.sum()

        return loss


class SoftTargetCrossEntropy(nn.Module):
    def __init__(self, normslized=False):
        super(SoftTargetCrossEntropy, self).__init__()
        self.normalized = normslized

    def forward(self, x, target):
        if self.normalized:
            loss = th.sum(-target * F.log_softmax(x, dim=-1), dim=-1) / th.sum(
                target, dim=-1
            )
        else:
            loss = th.sum(-target * F.log_softmax(x, dim=-1), dim=-1)
        return loss.mean()


class MultiWeightedLoss(nn.Module):
    def __init__(self, weights, criterion):
        super(MultiWeightedLoss, self).__init__()
        self.weights = weights
        self.criterion = criterion

    def forward(self, x, target):
        loss = 0
        for i, w in enumerate(self.weights):
            loss += w * self.criterion(x[i], target)

        return loss


class CLIPContrastive(nn.Module):
    def __init__(self):
        super(CLIPContrastive, self).__init__()
        self.loss_func = nn.CrossEntropyLoss()

    def forward(self, x):
        labels = th.arange(x.shape[0], device=x.device)

        loss_i = self.loss_func(x, labels)
        loss_t = self.loss_func(x.t(), labels)

        return (loss_i + loss_t) / 2.0


class UnifiedContrastive(nn.Module):
    """
    Unified Contrastive loss
    """

    def __init__(self):
        super(UnifiedContrastive, self).__init__()
        self.loss_func = SoftTargetCrossEntropy(normslized=True)

    def forward(self, x, targets=None):
        labels = th.arange(x.shape[0], device=x.device) if targets is None else targets

        loss_i = self.loss_func(x, labels)
        loss_t = self.loss_func(x.t(), labels)

        return (loss_i + loss_t) / 2.0


class DistributedChunkedHybridContrastive(nn.Module):
    """
    Efficient, distributed contrastive loss computation

    This is an alternative version of DistributedHybridContrastive
    that also chunks the local loss computation to save more memory.
    The underlying techniques are similar to the techniques for memory-efficient attention described in

    Self-Attention Does Not Need O(n^2) Memory
    Markus Rabe and Charles Staats
    see https://arxiv.org/abs/2112.05682v2

    Note that the forward function expects __local__ features (i.e., the features from this GPU)
    and takes care of gathering the features from all GPUs internally.
    For compatibility, the forward function expects __global__ targets.
    """

    def __init__(self):
        super(DistributedChunkedHybridContrastive, self).__init__()

    def forward(self, T, local_features_a, local_features_b, global_targets, training):
        def compute_loss_chunk(
            T, features_a, features_b, targets, chunk_start_idx, chunk_size
        ):
            # features_b = th.cat(features_b_chunks, dim=0)
            logits = T * features_a @ features_b.t()
            batch_size = features_a.shape[0]
            rank = th.distributed.get_rank()
            targets = (
                targets[rank * batch_size: (rank + 1) * batch_size].unsqueeze(1)
                == targets[
                    chunk_start_idx
                    * batch_size: (chunk_start_idx + chunk_size)
                    * batch_size
                ].unsqueeze(0)
            ).float()
            assert logits.shape == targets.shape
            logit_weighted_sum = th.sum(-targets * logits, dim=-1)
            logit_max = th.max(logits, dim=-1)[0]
            logit_exp_sum = th.sum(
                th.exp(logits - logit_max.detach().unsqueeze(1)), dim=-1
            )
            target_sum = th.sum(targets, dim=-1)
            return logit_weighted_sum, logit_max, logit_exp_sum, target_sum

        def compute_loss(T, features_a, global_features_b, targets, training):
            num_gpus = len(global_features_b)
            chunk_size = int(math.sqrt(num_gpus))

            logit_weighted_sum = []
            logit_max = []
            logit_exp_sum = []
            target_sum = []
            for chunk_start_idx in range(0, num_gpus, chunk_size):
                features_b_chunks = global_features_b[
                    chunk_start_idx: chunk_start_idx + chunk_size
                ]
                # TODO (rogmyr): It would be better to do this torch.cat inside of the activation checkpointing,
                # but I get PyTorch errors when I do that. Why?
                features_b = th.cat(features_b_chunks, dim=0)
                if training:
                    chunk_result = checkpoint(
                        compute_loss_chunk,
                        T,
                        features_a,
                        features_b,
                        targets,
                        chunk_start_idx,
                        chunk_size,
                    )
                else:
                    chunk_result = compute_loss_chunk(
                        T, features_a, features_b, targets, chunk_start_idx, chunk_size
                    )
                logit_weighted_sum.append(chunk_result[0])
                logit_max.append(chunk_result[1].detach())
                logit_exp_sum.append(chunk_result[2])
                target_sum.append(chunk_result[3])

            logit_weighted_sum = th.stack(logit_weighted_sum)
            logit_max = th.stack(logit_max)
            logit_exp_sum = th.stack(logit_exp_sum)
            target_sum = th.stack(target_sum)

            global_logit_weighted_sum = th.sum(logit_weighted_sum, dim=0)
            global_target_sum = th.sum(target_sum, dim=0)
            global_logit_max = th.max(logit_max, dim=0)[0]
            global_logit_exp_sum = th.sum(
                logit_exp_sum * th.exp(logit_max - global_logit_max.unsqueeze(0)), dim=0
            )

            loss = (
                global_logit_weighted_sum / global_target_sum
                + th.log(global_logit_exp_sum)
                + global_logit_max
            )

            return loss.mean()

        global_features_a = differentiable_all_gather(local_features_a)
        global_features_b = differentiable_all_gather(local_features_b)

        loss_i = compute_loss(
            T, local_features_a, global_features_b, global_targets, training
        )
        loss_t = compute_loss(
            T, local_features_b, global_features_a, global_targets, training
        )

        loss = (loss_i + loss_t) / 2.0

        # loss = differentiable_all_reduce(loss) / th.distributed.get_world_size()
        th.distributed.all_reduce(loss)
        loss /= th.distributed.get_world_size()

        return loss


def build_criterion(opt, train=True):
    if opt["AUG"].get("MIXUP_PROB", 0.0) > 0.0 and opt["LOSS"]["LOSS"] == "softmax":
        criterion = SoftTargetCrossEntropy() if train else nn.CrossEntropyLoss()
    elif (
        opt["LOSS"].get("LABEL_SMOOTHING", 0.0) > 0.0
        and opt["LOSS"]["LOSS"] == "softmax"
    ):
        criterion = LabelSmoothingCrossEntropy(opt["LOSS"]["LABEL_SMOOTHING"])
    elif opt["LOSS"]["LOSS"] == "softmax":
        criterion = nn.CrossEntropyLoss()
    elif opt["LOSS"]["LOSS"] == "sigmoid":
        criterion = nn.MultiLabelSoftMarginLoss(reduction="sum")
    elif opt["LOSS"]["LOSS"] == "focal":
        alpha = opt["LOSS"]["FOCAL"]["ALPHA"]
        gamma = opt["LOSS"]["FOCAL"]["GAMMA"]
        normalize = opt["LOSS"]["FOCAL"]["NORMALIZE"]
        criterion = FocalLoss(alpha, gamma, normalize)
    elif opt["LOSS"]["LOSS"] == "multisoftmax":
        criterion = MultiSoftmaxCrossEntropyLoss()
    elif opt["LOSS"]["LOSS"] == "clip_contrastive":
        criterion = CLIPContrastive()
    elif opt["LOSS"]["LOSS"] in ["sup_contrastive", "hybrid_contrastive", "UniCL"]:
        criterion = UnifiedContrastive()
    elif opt["LOSS"]["LOSS"] == "bce":
        criterion = (
            nn.BCEWithLogitsLoss() if train else nn.CrossEntropyLoss()
        )  # Note: Different behavior between training and evaluation.
    elif opt["LOSS"]["LOSS"] == "distributed_chunked_hybrid_contrastive":
        criterion = DistributedChunkedHybridContrastive()
    elif opt["LOSS"]["LOSS"] == "bce-loss":
        if train:
            criterion = th.nn.BCEWithLogitsLoss()
        else:
            criterion = nn.CrossEntropyLoss()

    # ------------- EXPERIMENTAL ###############
    elif opt["LOSS"]["LOSS"] in [
        "sup_contrastive_v2",
        "hybrid_contrastive_v2",
        "UniCL_v2",
    ]:
        criterion = UnifiedContrastiveV2()
    elif opt["LOSS"]["LOSS"] in [
        "sup_contrastive_stochastic",
        "hybrid_contrastive_stochastic",
        "UniCL_stochastic",
    ]:
        criterion = StochasticUnifiedContrastive()

    ##############################################

    else:
        raise ValueError("Unknown loss {}".format(opt["LOSS"]["LOSS"]))

    if opt["LOSS"].get("MULTI_OUTPUT", False):
        criterion = MultiWeightedLoss(opt["LOSS"]["WEIGHTS"], criterion)

    return criterion

    # --------------- EXPERIMENTAL ------------------#


class StochasticSoftTargetCrossEntropy(nn.Module):
    def __init__(self, normalized=False):
        super(StochasticSoftTargetCrossEntropy, self).__init__()
        self.normalized = normalized

    def forward(self, x, target):
        weights = th.rand(size=(target.size()[0], 1), device=x.device)
        weightsnorm = (weights / th.sum(weights)) * target.size()[0]

        if self.normalized:
            loss = weightsnorm * (
                th.sum(-target * F.log_softmax(x, dim=-1), dim=-1)
                / th.sum(target, dim=-1)
            )
        else:
            loss = weights * th.sum(-target * F.log_softmax(x, dim=-1), dim=-1)
        return loss.mean()


class StochasticUnifiedContrastive(nn.Module):
    """
    Unified Contrastive loss
    """

    def __init__(self):
        super(StochasticUnifiedContrastive, self).__init__()
        self.loss_func = StochasticSoftTargetCrossEntropy(normalized=True)

    def forward(self, x, targets=None):
        labels = th.arange(x.shape[0], device=x.device) if targets is None else targets

        loss_i = self.loss_func(x, labels)
        loss_t = self.loss_func(x.t(), labels)

        return (loss_i + loss_t) / 2.0


class SoftTargetLogLoss(nn.Module):
    def __init__(self, normslized=False):
        super(SoftTargetLogLoss, self).__init__()
        self.normalized = normslized

    def forward(self, x, target):
        if self.normalized:
            loss = (th.sum(x, dim=-1) / x.size()[-1]) + th.sum(
                -target * th.log(x), dim=-1
            ) / th.sum(target, dim=-1)
        else:
            loss = (th.sum(x, dim=-1)) + th.sum(-target * th.log(x), dim=-1)
        return loss.mean()


class UnifiedContrastiveV2(nn.Module):
    """
    Unified Contrastive loss
    """

    def __init__(self):
        super(UnifiedContrastiveV2, self).__init__()
        self.loss_func = SoftTargetLogLoss(normslized=True)

    def forward(self, x, targets=None):
        labels = th.arange(x.shape[0], device=x.device) if targets is None else targets

        loss_i = self.loss_func(x, labels)
        loss_t = self.loss_func(x.t(), labels)

        return (loss_i + loss_t) / 2.0

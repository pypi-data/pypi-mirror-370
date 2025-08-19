# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os

import numpy as np
import torch
import torch.nn as nn
import torchvision
from torch.utils.data import DataLoader
from typing import Tuple, Dict, List, Union
from torch import Tensor
from torch.utils.checkpoint import get_device_states, set_device_states
from azureml.acft.image.components.mainztrain.DataLoader import iterators
from azureml.acft.image.components.mainztrain.Trainers.MainzTrainer import MainzTrainer
from azureml.acft.image.components.mainztrain.Models.Tasks.BaseTask import BaseTask
from azureml.acft.image.components.mainztrain.Utils.GeneralUtils import AverageMeter
from azureml.acft.image.components.mainztrain.Utils.GeneralUtils import cast_batch_to_half
from azureml.acft.image.components.mainztrain.Utils.GeneralUtils import cast_batch_to_bf16
from azureml.acft.image.components.mainztrain.Utils.GeneralUtils import move_batch_to_device
from ..ImageDataLoader.tsv import TSVMeta
from ..Networks.GenericModel import model_wrappers
from ..Networks.UniCLModel import build_unicl_model
from ..Criteria import build_criterion
from ..ImageDataLoader import build_dataloader
from ..ImageDataLoader import build_multitask_dataloader
from ..ImageDataLoader import build_transforms
from ..ImageDataLoader import IMAGENET_CLASSES
from ..ImageDataLoader import IMAGENET_DEFAULT_TEMPLATES
from ..ImageDataLoader import ZipData

# from ..Utils import analysis_model
from ..Utils import gather_tensors
from ..Utils import is_main_process

from ..ImageDataLoader.tsv import TSVImageTextDatasetV2

import sklearn.metrics

logger = logging.getLogger(__name__)


@torch.no_grad()
def accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    if isinstance(output, list):
        output = output[-1]

    n_classes = output.size()[1]
    maxk = min(max(topk), n_classes)
    batch_size = target.size(0)
    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    correct = pred.eq(target.reshape(1, -1).expand_as(pred))

    res = []
    for k in topk:
        correct_k = correct[:k].reshape(-1).float().sum(0, keepdim=True)
        res.append(correct_k.mul_(100.0 / batch_size).item())
    return res


@torch.no_grad()
def translate(text, key):
    import requests
    import uuid

    # Add your key and endpoint
    # key = args.key
    endpoint = "https://api.cognitive.microsofttranslator.com/"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "westus2"

    path = "/translate"
    constructed_url = endpoint + path

    params = {"api-version": "3.0", "to": ["en"]}

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    # You can pass more than one object in body.
    body = [{"text": text}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    return response[0]["translations"][0]["text"]


class UniCLTask(BaseTask):
    def __init__(self, opt):
        super().__init__(opt)

    def set_up_model(
        self,
    ) -> Tuple[List[str], Dict[str, nn.Module], Dict[str, nn.Module]]:
        """
        Set up raw_modules and criteria

        This method initializes raw_modules and criteria as dictionaries containing the
        instances of `BaseModel` and `BaseCriterion`. raw_modules are trainable models, while
        criteria are used for loss calculation and do not contain trainable parameters.

        Returns:
            Tuple: (module_names, raw_modules, criteria)
                module_names: a list of module names in the raw_modules
                raw_modules: a dictionary containing models of class `BaseModel`
                criteria: a dictionary containing criteria of class `BaseCriterion`
        """
        module_name = "default"

        # register apex ops
        if self._opt.get("AMP", "PYTORCH") == "APEX":
            from apex import amp

            amp.register_half_function(torch, "einsum")
            amp.register_half_function(torch, "bmm")

        model = build_unicl_model(self._opt)

        model.train()
        model.cuda()

        raw_modules = {
            module_name: model_wrappers(self._opt.get("MODEL_WRAPPER", "GenericModel"))(
                self._opt, model
            )
        }

        if is_main_process():

            if self._opt.get("MODEL_SIZE_REPORT", False):
                logger.info("**************** Image encoder summary ****************")
                dump_input_size = (1, 3, *self._opt["IMAGE_ENCODER"]["IMAGE_SIZE"])
                dump_input = torch.rand(dump_input_size).cuda()
                raw_modules["default"].analysis_model(
                    "model.image_encoder", dump_input, self._opt["VERBOSE"]
                )
                logger.info("**************** Image encoder summary ****************")

                logger.info(
                    "**************** Language encoder summary ****************"
                )
                dump_input_size = (1, self._opt["LANG_ENCODER"]["CONTEXT_LENGTH"])
                dump_input = torch.rand(dump_input_size).type(torch.LongTensor).cuda()
                raw_modules["default"].analysis_model(
                    "model.lang_encoder", dump_input, self._opt["VERBOSE"]
                )
                logger.info(
                    "**************** Language encoder summary ****************"
                )
            else:
                logger.info("***************** SKIP MODEL SUMMARY ******************")

        criterion_train = build_criterion(self._opt)
        # criterion_eval = build_criterion(self._opt, train=False)

        criterions = {
            "train": criterion_train,
            # "eval": criterion_eval
        }

        return [module_name], raw_modules, criterions

    def get_zeroshot_eval_generator(self, distributed):
        eval_dataset = self._opt["ZEROSHOT_EVAL_DATASET"]
        data_format = eval_dataset.get("FORMAT", "jpg")

        transforms = build_transforms(self._opt, False)
        if data_format == "jpg":
            dataset = torchvision.datasets.ImageFolder(
                os.path.join(eval_dataset["ROOT"], "val"), transform=transforms
            )
        elif data_format == "vision-datasets":
            import pathlib
            from vision_datasets import DatasetHub, Usages
            from ..ImageDataLoader.vision_dataset import MultiClassTorchDatasetWrapper

            dataset_name = eval_dataset["SPLIT"]
            manifest_dataset = DatasetHub(
                pathlib.Path(eval_dataset["DATA_REG_JSON_PATH"]).read_text()
            ).create_manifest_dataset(
                container_sas=eval_dataset["BLOB_CONTAINER"],
                local_dir=eval_dataset["ROOT"],
                name=dataset_name,
                usage=Usages.TEST_PURPOSE,
            )
            dataset = MultiClassTorchDatasetWrapper(manifest_dataset, transforms)
        elif data_format == "zip":
            dataset = ZipData(
                path=eval_dataset["ZIP_FILE"],
                map_file=eval_dataset["ZIP_MAP_FILE"],
                transform=transforms,
            )
        else:
            logger.error(f"Unknown evaluation data format: {data_format}")
            raise ValueError(f"Unknown evaluation data format: {data_format}")

        sampler = (
            torch.utils.data.distributed.DistributedSampler(dataset, shuffle=False)
            if distributed
            else None
        )
        data_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=self._opt["TEST"]["BATCH_SIZE_PER_GPU"],
            shuffle=False,
            num_workers=self._opt["WORKERS"],
            pin_memory=self._opt["PIN_MEMORY"],
            sampler=sampler,
            drop_last=False,
        )

        return data_loader

    def get_batch_generator(
        self, trainer: MainzTrainer, dataset: str, is_evaluation: bool
    ) -> Union[DataLoader, iterators.CheckpointableIterator]:
        """
        Get a batch generator from the task for "train", "dev", or "test" set.
        Make sure to use 'world_size' and 'rank' info in opt when preparing batch generator
        for distributed training.

        Args:
            trainer (MainzTrainer): trainer object
            dataset (str): "evaluation dataset"
            is_evaluation (bool): whether the batch generator is for evaluation or training

        Returns:
            Iterable: an iterable of class `DataLoader` that yields batches
        """
        distributed = self._opt["world_size"] > 1

        if not is_evaluation:
            if not hasattr(self, "train_loader"):
                if self._opt.get("MULTITASK_DATALOADER", None) is not None:
                    dataloader = build_multitask_dataloader(
                        self._opt, True, distributed
                    )
                    logger.info(
                        f"num of train samples: {[(k, len(v.dataset)) for k, v in dataloader.dataloaders.items()]}"
                    )
                else:
                    dataloader = build_dataloader(self._opt, True, distributed)
                    logger.info(f"num of train samples: {len(dataloader.dataset)}")
                self.train_loader = dataloader
            else:
                dataloader = self.train_loader

            # temp solution for lr scheduler
            steps_total = len(self.train_loader)
            steps_acc = self._opt["GRADIENT_ACCUMULATE_STEP"]
            steps_update = steps_total // steps_acc
            self._opt["OPTIM_STEPS_PER_EPOCH"] = steps_update

            if "MAX_NUM_EPOCHS" in self._opt:
                self._opt["LR_SCHEDULER_PARAMS"][
                    "steps_update_per_epoch"
                ] = steps_update
            if (
                self._opt.get("SAVE_PER_OPTIM_STEPS")
                and self._opt["SAVE_PER_OPTIM_STEPS"] < 0
            ):
                self._opt["SAVE_PER_OPTIM_STEPS"] = steps_total // steps_acc * steps_acc
        elif dataset in ["coco-caption-val2017", "coco-caption-test2014"]:
            # COCO-caption validation dataset path is specified in ['DATA_SET']['TEST_SET']
            dataloader = build_dataloader(self._opt, False, False)
        else:
            if not hasattr(self, "valid_loader"):
                dataloader = self.get_zeroshot_eval_generator(distributed)
                self.valid_loader = dataloader
                logger.info(f"num of val samples: {len(dataloader.dataset)}")
            else:
                dataloader = self.valid_loader

        return dataloader

    @staticmethod
    def forward_func(trainer, batch):
        # x, y, target = batch
        x, y, *target = batch

        if len(target) > 0:
            # Sup-contrastive data
            target = target[0]
        else:
            # Contrastive-only data leveraged in UniCL objective
            target = torch.zeros(x.shape[0], device=x.device)

        y = dict(map(lambda kv: (kv[0], kv[1].cuda(non_blocking=True)), y.items()))

        trainer.modules["default"].train()
        features_image, features_text, T = trainer.modules["default"](x, y)

        if trainer.opt["UNICL_MODEL"]["GATHER_TENSORS"]:
            features_image_all = gather_tensors(features_image)
            features_text_all = gather_tensors(features_text)
            logits_image_text = T * features_image_all @ features_text_all.t()

            # re-assign target labels
            target_all = gather_tensors(target)
            target_all = target_all[target_all >= 0]
            target_modified = target_all.clone().view(-1)
            supervised_data = target_all[target_all > 0]
            max_label = supervised_data.max() if supervised_data.numel() else 0
            target_modified[target_all == 0] = (
                max_label
                + torch.arange(0, (target_all == 0).sum()).type_as(target_all)
                + 1
            )
        else:
            logits_image_text = T * features_image @ features_text.t()

            # re-assign target labels
            target = target[target >= 0]
            target_modified = target.clone().view(-1)  # B x 1
            supervised_data = target[target > 0]
            max_label = supervised_data.max() if supervised_data.numel() else 0
            target_modified[target == 0] = (
                max_label
                + torch.arange(0, (target == 0).sum()).type_as(target_modified)
                + 1
            )

        if trainer.opt["LOSS"]["LOSS"] == "distributed_chunked_hybrid_contrastive":
            assert (
                trainer.opt["UNICL_MODEL"]["GATHER_TENSORS"] is True
            ), "DistributedHybridContrastive requires gather=True"
            training = trainer.opt["trainer_mode"] == "train"
            loss = trainer.criteria["train"](
                T, features_image, features_text, target_modified, training
            )
        else:
            targets = (
                target_modified.view(-1, 1) == target_modified.view(1, -1)
            ).float()
            loss = trainer.criteria["train"](logits_image_text, targets)

        if trainer.opt.get("SCALE_LOSS_IN_FORWARD", False):
            loss *= trainer.opt["GRADIENT_ACCUMULATE_STEP"]

        return loss

    @staticmethod
    def forward_acc_func(trainer, batch):
        # x, y, target = batch

        x, y, *target = batch

        if len(target) > 0:
            # Sup-contrastive data
            target = target[0]
        else:
            # Contrastive-only data leveraged in UniCL objective
            target = torch.zeros(x.shape[0], device=x.device)

        trainer.modules["default"].train()
        features_image, features_text, T = trainer.modules["default"](x, y)

        return features_image, features_text, T, target

    def reset_grad_cache(self):
        self.features_image_grad_cache = []
        self.features_text_grad_cache = []
        self.T_grad_cache = None

    def build_grad_cache(
        self, trainer, features_image_acc, features_text_acc, T, targets_acc
    ):
        # calculate loss from output features gathered from all mini batches across grad accumulation steps and GPUs,
        # cache gradients on all mini batch output features, and report the loss
        features_image_acc = [f.detach().requires_grad_() for f in features_image_acc]
        features_text_acc = [f.detach().requires_grad_() for f in features_text_acc]
        targets_acc = [f.detach() for f in targets_acc]
        T = T.detach().requires_grad_()

        features_image = torch.cat(features_image_acc, dim=0)
        features_text = torch.cat(features_text_acc, dim=0)
        targets_acc = torch.cat(targets_acc, dim=0)
        assert trainer.opt["UNICL_MODEL"]["GATHER_TENSORS"]
        features_image = gather_tensors(features_image)
        features_text = gather_tensors(features_text)
        targets_acc = gather_tensors(targets_acc)

        targets_acc = targets_acc[targets_acc >= 0]
        targets_modified = targets_acc.clone().view(-1)
        supervised_data = targets_acc[targets_acc > 0]
        max_label = supervised_data.max() if supervised_data.numel() else 0
        targets_modified[targets_acc == 0] = (
            max_label
            + torch.arange(0, (targets_acc == 0).sum()).type_as(targets_acc)
            + 1
        )
        targets = (targets_modified.view(-1, 1) == targets_modified.view(1, -1)).float()

        logits_image_text = T * features_image @ features_text.t()

        loss = trainer.criteria["train"](logits_image_text, targets)
        loss_val = loss.detach().item()

        if trainer.opt["FP16"]:
            # When using AMP, we need to manually scale the loss and unscale the feature grads we cache,
            # in order to avoid lossing precision due to FP16.
            # Ideally, trainer implementation details should not be exposed here, but it seems inevitable in this case.
            if trainer.opt["DEEPSPEED"]:
                loss_scale = trainer.optimizers["default"].cur_scale
                loss = (loss.float()) * loss_scale
            else:
                if trainer.opt["AMP"] == "APEX":
                    from apex import amp

                    loss_scale = amp._amp_state.loss_scalers[0].loss_scale()
                    loss = (loss.float()) * loss_scale
                else:  # trainer.opt['AMP'] == 'PYTORCH'
                    loss = trainer.grad_scaler.scale(loss)

        loss.backward()

        self.features_image_grad_cache = [f.grad.detach() for f in features_image_acc]
        self.features_text_grad_cache = [f.grad.detach() for f in features_text_acc]
        self.T_grad_cache = T.grad.detach()

        if trainer.opt["FP16"]:
            # When using AMP, we need to manually scale the loss and unscale the feature grads we cache,
            # in order to avoid lossing precision due to FP16.
            # Ideally, trainer implementation details should not be exposed here, but it seems inevitable in this case.
            if trainer.opt["DEEPSPEED"]:
                grad_unscale = 1.0 / loss_scale
            else:
                if trainer.opt["AMP"] == "APEX":
                    grad_unscale = 1.0 / loss_scale
                else:  # trainer.opt['AMP'] == 'PYTORCH'
                    grad_unscale = (
                        trainer.grad_scaler._scale.double().reciprocal().float().item()
                    )
            for grad_cache in [
                self.features_image_grad_cache,
                self.features_text_grad_cache,
            ]:
                for g in grad_cache:
                    g.mul_(grad_unscale)
            self.T_grad_cache.mul_(grad_unscale)

        return loss_val

    def train_step(
        self,
        trainer: MainzTrainer,
        batch,
        grad_acc_batches: List,
        grad_acc_index: int,
        is_distributed: bool,
        is_gradient_accumulation_boundary: bool,
    ) -> Tuple[Dict[str, float], Dict[str, int], Dict]:
        """
        train_step method defines the logics of one training step in the training loop.

        It calls the basic building blocks provided by MainzTrainer:​
        `trainer.forward_pass()​`
        `trainer.backward_pass()​`
        `trainer.step()​`
        Please see MainzTrainer for the definition of these methods.

        trainer.forward_pass() and trainer.backward_pass() can be called multiple times on one or more modules.​
        trainer.step() should be called on every module once and only once.

        Args:
            trainer (MainzTrainer): trainer object
            batch: one batch of training data from the batch generator, after being moved to device
            grad_acc_batches (list): a list of batches (on CPU) in the same gradient accumulation boundaries
            grad_acc_index (int): the index of the current batch in the grad_acc_batches
            is_distributed (bool): True if it is a distributed job, and modules are wrapped in DeepSpeed or DDP
            is_gradient_accumulation_boundary (bool):

            True if current iteration is at the boundary of gradient accumulation
            this and is_distributed can be used together to determine if gradient
            allreduce can be skiped or not.

        Returns:
            Tuple: (loss_info, sample_size_info, extra_info)
                loss_info (dict): a dictionary of loss values to be logged and plotted.
                It can be any losses user want to be aggregated and logged,
                not limited to the losses used by the backward pass.
                Losses in mini-batches of same effective batch are averaged.
                sample_size_info (dict): a dictionary of sample sizes to be logged and plotted.
                Sizes in mini-batches of same effective batch are summed.
                extra_info (dict): a dictionary of additional info to be logged.
        """
        loss_info, sample_size_info, extra_info = {}, {}, {}
        skip_gradient_sync = is_distributed and (not is_gradient_accumulation_boundary)
        # loss = trainer.forward_pass(self.forward_func, batch, skip_gradient_sync)
        # loss_info = {'train_loss': loss.detach().item()}

        if (
            self._opt["GRADIENT_ACCUMULATE_STEP"] == 1
            or not self._opt["UNICL_MODEL"]["GATHER_TENSORS"]
        ):
            loss = trainer.forward_pass(self.forward_func, batch, skip_gradient_sync)
            loss, loss_info = trainer.raw_modules["default"].get_loss_info(loss)
        else:
            if grad_acc_index == 0:
                assert not is_gradient_accumulation_boundary
                self.rnd_states = []
                self.loss_val = 0
                self.reset_grad_cache()

                features_image_acc = []
                features_text_acc = []
                targets_acc = []
                with torch.no_grad():
                    # collect output features from all mini batches on this GPU
                    # record their torch random contexts
                    for tmp_batch in grad_acc_batches:
                        tmp_batch = move_batch_to_device(tmp_batch, self._opt["device"])
                        self.rnd_states.append(
                            RandContext(*get_input_tensors(tmp_batch))
                        )
                        tmp_features_image, tmp_features_text, tmp_T, tmp_targets = (
                            trainer.forward_pass(
                                self.forward_acc_func, tmp_batch, skip_gradient_sync
                            )
                        )
                        features_image = tmp_features_image.detach()
                        features_text = tmp_features_text.detach()
                        targets = tmp_targets.detach()
                        T = tmp_T.detach()
                        del tmp_features_image, tmp_features_text, tmp_T, tmp_targets
                        features_image_acc.append(features_image)
                        features_text_acc.append(features_text)
                        targets_acc.append(targets)
                # calculate loss from output features gathered from all
                # mini batches across grad accumulation steps and GPUs,
                # cache gradients on all mini batch output features, and report the loss
                self.loss_val = self.build_grad_cache(
                    trainer, features_image_acc, features_text_acc, T, targets_acc
                )

            with self.rnd_states[grad_acc_index]:
                # redo the forward under the same torch random context as
                # when building the grad cache, this time requiring grads
                features_image, features_text, T, _ = trainer.forward_pass(
                    self.forward_acc_func, batch, skip_gradient_sync
                )
            loss_info = {"train_loss": self.loss_val}
            # use a surrogate loss to apply cached grads to the output features
            surrogate_loss = torch.dot(
                features_image.flatten(),
                self.features_image_grad_cache[grad_acc_index].flatten(),
            )
            surrogate_loss += torch.dot(
                features_text.flatten(),
                self.features_text_grad_cache[grad_acc_index].flatten(),
            )
            surrogate_loss += T * self.T_grad_cache
            loss = surrogate_loss

        sample_size_info = {"num_samples": batch[0].size()[0]}
        trainer.backward_pass(loss, skip_gradient_sync, module_names=["default"])
        trainer.step(is_gradient_accumulation_boundary, module_name="default")

        return loss_info, sample_size_info, extra_info

    @staticmethod
    @torch.no_grad()
    def zeroshot_classifier(classnames, templates, model, max_length=77):
        zeroshot_weights = []
        for classname in classnames:
            texts = [template.format(classname) for template in templates]

            texts = model.tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            texts = dict(
                map(lambda kv: (kv[0], kv[1].cuda(non_blocking=True)), texts.items())
            )
            class_embeddings = model.encode_text(texts)
            class_embedding = class_embeddings.mean(dim=0)
            class_embedding /= class_embedding.norm()
            zeroshot_weights.append(class_embedding)
        zeroshot_weights = torch.stack(zeroshot_weights, dim=1).cuda()

        return zeroshot_weights

    @torch.no_grad()
    def evaluate_model(
        self, trainer: MainzTrainer, dataset_label: str, save_folder, label=""
    ) -> Tuple[Dict, Dict[str, float], bool]:
        """
        Evaluate the module (usually the trainer.raw_modules) on the selected dataset.
        It is called on all ranks. The returned `got_better_score` must be consistant across all the ranks.
        It also maintains and updates self.eval_best_results and self.eval_best_scores.

        Args:
            trainer (MainzTrainer): trainer object
            dataset_label (str): "dev", or "test"
            save_folder: path to save the results
            label: prefix label for saving result files

        Returns:
            Tuple: (results, scores, got_better_score)
                results (dict): contains evaluation results
                scores (dict): contains evaluation scores
                got_better_score (bool): True if better evaluation score is achieved
                    It must be consistant across all the ranks.
        """
        if dataset_label in [
            "coco-caption",
            "coco-caption-val2017",
            "coco-caption-test2014",
        ]:
            scores, scores, got_better_score = self.evaluate_coco_zeroshot(
                trainer, dataset_label, save_folder, label
            )
        elif dataset_label in ["cls-zeroshot-eval", "dev", "imagenet"]:
            scores = {}
            got_better_flag = False
            got_better_score = False
            logger.info("Running search for eval datasets V2...")
            for confkey in self._opt.keys():

                if confkey.startswith("ZEROSHOT_EVAL_DATASET"):
                    eval_dataset = self._opt["ZEROSHOT_EVAL_DATASET"].get(
                        "DATASET", dataset_label
                    )
                    scoreszero, scoreszero, gbsz = self.evaluate_custom_vision_zeroshot(
                        trainer, eval_dataset, save_folder, label
                    )

                    scores.update(scoreszero)

                    # By default track this evaluation.
                    if not got_better_flag:
                        got_better_flag = True
                        got_better_score = gbsz
                        logger.info("EVALUATION V2 IS TRACKING: " + confkey)

                elif (
                    confkey.startswith("KNNSHOT")
                    or confkey.startswith("EVALDATASET")
                    or confkey.startswith("STATICEVAL")
                    or confkey.startswith("FIXEDEVAL")
                ):
                    logger.info("Running evaluation on: " + confkey + " ...")
                    knn_eval = self._opt[confkey].get("DATASET", dataset_label)
                    trackmetric = self._opt[confkey].get("TRACK_METRIC", None)
                    scoresknn, scoresknn, gbsknn = (
                        self.evaluate_static_search_classification_regression(
                            cfg=self._opt,
                            trainer=trainer,
                            dataset=knn_eval,
                            save_folder=save_folder,
                            label=label,
                            knnconfkey=confkey,
                            zeroshot_mode=self._opt[confkey].get("ZS_MODE", 0),
                            trackmetricbestscore=trackmetric,
                        )
                    )
                    scores.update(scoresknn)

                    if (not got_better_flag) and (trackmetric is not None):
                        got_better_flag = True
                        got_better_score = gbsknn
                        logger.info(
                            "EVALUATION V2 IS TRACKING: "
                            + confkey
                            + ", WITH METRIC: "
                            + str(trackmetric)
                        )

        elif dataset_label in ["vision-benchmark"]:
            scores = {}
            got_better_score = False
            for dataset in trainer.opt.get("VISION_BENCHMARK_DATASETS", []):
                score, score, _ = self.evaluate_vision_datasets_zeroshot(
                    trainer, dataset, save_folder, label
                )
                logger.info(f"zero-shot evaluation: {score}")
                scores.update({f"{dataset}-{k}": v for k, v in score.items()})
        elif dataset_label in ["all"]:
            scores_coco, scores_coco, _ = self.evaluate_coco_zeroshot(
                trainer, "coco-caption-test2014", save_folder, label
            )
            scores_in, scores_in, got_better_score = self.evaluate_imagenet_zeroshot(
                trainer, "imagenet", save_folder, label
            )

            scores = {**scores_coco, **scores_in}
        elif dataset_label in ["coco-caption-universal"]:
            scores, scores, got_better_score = self.evaluate_coco_universal(trainer)
        elif dataset_label in ["vision-benchmark-matching"]:
            scores, scores, got_better_score = self.evaluate_vision_datasets_matching(
                trainer
            )

        return scores, scores, got_better_score

    @torch.no_grad()
    def evaluate_imagenet_zeroshot(
        self, trainer: MainzTrainer, dataset_label: str, save_folder, label=""
    ) -> Tuple[Dict, Dict[str, float], bool]:
        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        eval_batch_gen = self.get_batch_generator(
            trainer, dataset_label, is_evaluation=True
        )

        classnames = ""
        templates = ""
        if dataset_label in ["imagenet"]:
            classnames = IMAGENET_CLASSES
            templates = IMAGENET_DEFAULT_TEMPLATES
        else:
            raise ValueError(f"Unknown dataset: {dataset_label}")

        zeroshot_weights = self.zeroshot_classifier(
            classnames,
            templates,
            model_without_ddp,
            max_length=self._opt["LANG_ENCODER"].get("CONTEXT_LENGTH", 77),
        )

        top1 = AverageMeter()
        top5 = AverageMeter()

        for i, (x, y) in enumerate(eval_batch_gen):
            x = x.cuda(non_blocking=True)
            y = y.cuda(non_blocking=True)
            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            elif model_without_ddp.dtype is torch.bfloat16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_bf16(x)
                y = cast_batch_to_bf16(y)
            features_image = model_without_ddp.encode_image(x)
            logits = 100.0 * features_image @ zeroshot_weights

            prec1, prec5 = accuracy(logits, y, (1, 5))
            top1.update(prec1, x.size(0))
            top5.update(prec5, x.size(0))

        if self._opt["world_size"] > 1:
            tmp_tensor = torch.tensor(
                [top1.sum, top5.sum, top1.count], device=self._opt["device"]
            )
            torch.distributed.all_reduce(tmp_tensor, torch.distributed.ReduceOp.SUM)
            top1_sum, top5_sum, count = tmp_tensor.tolist()
        else:
            top1_sum = top1.sum
            top5_sum = top5.sum
            count = top1.count

        scores = {"top1": top1_sum / count, "top5": top5_sum / count}

        best_score = self.eval_best_scores.get("top1", 0)
        got_better_score = scores["top1"] > best_score

        if got_better_score:
            self.eval_best_scores = scores.copy()

        return scores, scores, got_better_score

    @torch.no_grad()
    def evaluate_cls_zeroshot(
        self, eval_batch_gen, model_without_ddp, classnames, templates, metric
    ):
        zeroshot_weights = self.zeroshot_classifier(
            classnames,
            templates,
            model_without_ddp,
            max_length=self._opt["LANG_ENCODER"].get("CONTEXT_LENGTH", 77),
        )

        features_image_all = []
        labels_all = []
        # import time

        for i, batch in enumerate(eval_batch_gen):
            x, y = batch[0], batch[1]
            x = x.cuda(non_blocking=True)
            y = y.cuda(non_blocking=True)
            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            elif model_without_ddp.dtype is torch.bfloat16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_bf16(x)
                y = cast_batch_to_bf16(y)

            features_image = model_without_ddp.encode_image(x)
            # logits = 100. * features_image @ zeroshot_weights

            features_image_all.append(features_image)
            labels_all.append(y)

        features_image_all = torch.cat(features_image_all, dim=0)
        labels_all = torch.cat(labels_all, dim=0)
        logits_all = 100.0 * features_image_all @ zeroshot_weights
        if self._opt["world_size"] > 1:
            labels_all = gather_tensors(labels_all)
            logits_all = gather_tensors(logits_all)

        score = metric(
            labels_all.squeeze().cpu().detach().numpy(),
            logits_all.cpu().detach().numpy(),
        )

        return score, score, False

    @torch.no_grad()
    def evaluate_custom_vision_zeroshot(
        self, trainer: MainzTrainer, dataset: str, save_folder, label=""
    ) -> Tuple[Dict, Dict[str, float], bool]:
        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        eval_batch_gen = self.get_batch_generator(trainer, dataset, is_evaluation=True)

        classnames = []
        templates = []
        if dataset in ["imagenet"]:
            classnames = IMAGENET_CLASSES
            templates = IMAGENET_DEFAULT_TEMPLATES
        else:
            eval_dataset = self._opt["ZEROSHOT_EVAL_DATASET"]
            if eval_dataset["FORMAT"] == "vision-datasets":
                import pathlib
                from vision_datasets import DatasetHub, Usages

                dataset_name = eval_dataset["SPLIT"]
                dataset_manifest = DatasetHub(
                    pathlib.Path(eval_dataset["DATA_REG_JSON_PATH"]).read_text()
                ).create_dataset_manifest(
                    container_sas=eval_dataset["BLOB_CONTAINER"],
                    local_dir=eval_dataset["ROOT"],
                    name=dataset_name,
                    usage=Usages.TEST_PURPOSE,
                )[
                    0
                ]
                classnames = dataset_manifest.labelmap
            else:
                with open(eval_dataset["LABEL_FILE"], "r") as f:
                    for la in f:
                        classnames.append(la.strip())

            if eval_dataset.get("TEMPLATES", None):
                with open(eval_dataset["TEMPLATES"], "r") as f:
                    for la in f:
                        templates.append(la.strip())
            else:
                templates = IMAGENET_DEFAULT_TEMPLATES

            # raise ValueError(f'Unknown dataset: {dataset_label}')

        zeroshot_weights = self.zeroshot_classifier(
            classnames,
            templates,
            model_without_ddp,
            max_length=self._opt["LANG_ENCODER"].get("CONTEXT_LENGTH", 77),
        )

        top1 = AverageMeter()
        top5 = AverageMeter()
        import time

        inference_time = 0
        t0 = time.time()
        n_samples = 0
        for i, (x, y) in enumerate(eval_batch_gen):
            x = x.cuda(non_blocking=True)
            y = y.cuda(non_blocking=True)
            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            elif model_without_ddp.dtype is torch.bfloat16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_bf16(x)
                y = cast_batch_to_bf16(y)
            t1 = time.time()
            features_image = model_without_ddp.encode_image(x)
            logits = 100.0 * features_image @ zeroshot_weights
            t2 = time.time()
            inference_time += t2 - t1
            prec1, prec5 = accuracy(logits, y, (1, 5))
            top1.update(prec1, x.size(0))
            top5.update(prec5, x.size(0))
            n_samples += x.size(0)

        logger.info(
            f"""Total evaluation time  {time.time() - t0}
            over {n_samples}, model inference time
            {inference_time / n_samples * 1000} ms/image."""
        )
        if self._opt["world_size"] > 1:
            tmp_tensor = torch.tensor(
                [top1.sum, top5.sum, top1.count], device=self._opt["device"]
            )
            torch.distributed.all_reduce(tmp_tensor, torch.distributed.ReduceOp.SUM)
            top1_sum, top5_sum, count = tmp_tensor.tolist()
        else:
            top1_sum = top1.sum
            top5_sum = top5.sum
            count = top1.count

        scores = {"top1": top1_sum / count, "top5": top5_sum / count}

        best_score = self.eval_best_scores.get("top1", 0)
        got_better_score = scores["top1"] > best_score

        if got_better_score:
            self.eval_best_scores = scores.copy()

        return scores, scores, got_better_score

    @torch.no_grad()
    def evaluate_vision_datasets_zeroshot(
        self, trainer: MainzTrainer, dataset_label: str, save_folder, label=""
    ):
        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        from vision_benchmark.config import config
        from vision_benchmark.config.default import _update_config_from_file
        from vision_benchmark.commands.eval import alexandar_leaderboard

        vision_benchmark_root = trainer.opt.get(
            "VISION_BENCHMARK_ROOT", "Vision-Benchmark"
        )

        _update_config_from_file(
            config,
            os.path.join(
                vision_benchmark_root,
                "vision_benchmark",
                alexandar_leaderboard[dataset_label],
            ),
        )
        # TODO: we omit the correction of AUG.MIXUP because currently we do not have it in CLIP

        config.defrost()
        config.DATASET.CENTER_CROP = trainer.opt["TEST"]["CENTER_CROP"]
        image_size = (
            trainer.opt["IMAGE_ENCODER"]["IMAGE_SIZE"][0],
            trainer.opt["IMAGE_ENCODER"]["IMAGE_SIZE"][1],
        )
        config.DATASET.IAMGE_SIZE = image_size
        config.TRAIN.IAMGE_SIZE = image_size
        config.TEST.IAMGE_SIZE = image_size
        config.freeze()

        from vision_benchmark.evaluation.feature import (
            build_image_loader,
            get_class_names,
            get_templates,
        )

        distributed = True if trainer.opt["world_size"] > 1 else False
        _, _, eval_batch_gen = build_image_loader(
            config,
            test_split_only=True,
            distributed=distributed,
            local_rank=trainer.opt["local_rank"],
        )  # only load test data: train, val, test

        classnames = get_class_names(dataset_label)
        templates = get_templates(dataset_label)

        from vision_benchmark.evaluation.metric import get_metric

        metric = get_metric(config.TEST.METRIC)

        scores, _, _ = self.evaluate_cls_zeroshot(
            eval_batch_gen,
            model_without_ddp,
            classnames,
            templates,
            metric,
        )
        scores_dic = {config.TEST.METRIC: scores}
        return scores_dic, scores_dic, False

    @torch.no_grad()
    def evaluate_coco_zeroshot(
        self, trainer: MainzTrainer, dataset_label: str, save_folder, label=""
    ) -> Tuple[Dict, Dict[str, float], bool]:

        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        eval_batch_gen = self.get_batch_generator(
            trainer, dataset_label, is_evaluation=True
        )

        features_image = []
        features_text = []
        num_captions_per_img = 5

        for i, (x, y, _) in enumerate(eval_batch_gen):
            x = x.cuda(non_blocking=True)
            y = dict(map(lambda kv: (kv[0], kv[1].cuda(non_blocking=True)), y.items()))

            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            elif model_without_ddp.dtype is torch.bfloat16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_bf16(x)
                y = cast_batch_to_bf16(y)

            features_image.append(
                model_without_ddp.encode_image(x)
                # gather_tensors(model_without_ddp.encode_image(x)).cpu()
            )
            if num_captions_per_img > 1:
                B, N, C = y["input_ids"].shape
                y = dict(map(lambda kv: (kv[0], kv[1].reshape(B * N, C)), y.items()))
            features_text.append(model_without_ddp.encode_text(y))

        features_image = torch.cat(features_image)
        features_text = torch.cat(features_text)

        i2t_similarities = features_image @ features_text.t()

        i2t_ranks = []
        for i, sim in enumerate(i2t_similarities.cpu().numpy()):
            inds = np.argsort(sim)[::-1]
            for r, ind in enumerate(inds):
                if i * num_captions_per_img <= ind < (i + 1) * num_captions_per_img:
                    rank = r
                    break
            i2t_ranks.append(rank)

        rank = [1, 5]
        i2t_accs = [sum([_ < r for _ in i2t_ranks]) / len(i2t_ranks) for r in rank]

        t2i_similarities = features_text @ features_image.t()

        t2i_ranks = []
        for i, sim in enumerate(t2i_similarities.cpu().numpy()):
            inds = np.argsort(sim)[::-1]
            for r, ind in enumerate(inds):
                if i // num_captions_per_img == ind:
                    rank = r
                    break
            t2i_ranks.append(rank)

        rank = [1, 5]
        t2i_accs = [sum([_ < r for _ in t2i_ranks]) / len(t2i_ranks) for r in rank]

        logger.info(
            "=> I2T Retrieval: {:.4f} @ R1, {:.4f} @ R5".format(
                i2t_accs[0], i2t_accs[1]
            )
        )
        logger.info(
            "=> T2I Retrieval: {:.4f} @ R1, {:.4f} @ R5".format(
                t2i_accs[0], t2i_accs[1]
            )
        )

        scores = {"i2t_accs": i2t_accs[0], "t2i_accs": t2i_accs[0]}

        best_score = self.eval_best_scores.get("t2i_accs", 0)
        got_better_score = scores["t2i_accs"] > best_score

        if got_better_score:
            self.eval_best_scores = scores.copy()

        return scores, scores, got_better_score

    @torch.no_grad()
    def evaluate_coco_universal(self, trainer):
        from ..ImageDataLoader.build import build_coco_caption_universal_dataloader

        eval_batch_gen = build_coco_caption_universal_dataloader(
            trainer.opt, is_train=False, distributed=False
        )
        features_image = []
        features_text = []
        num_captions_per_img = trainer.opt["COCO_CAPTION_UNIVERSAL"]["NUM_CAPTIONS"]

        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        for i, (x, y) in enumerate(eval_batch_gen):
            x = x.cuda(non_blocking=True)
            y = dict(map(lambda kv: (kv[0], kv[1].cuda(non_blocking=True)), y.items()))

            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            elif model_without_ddp.dtype is torch.bfloat16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_bf16(x)
                y = cast_batch_to_bf16(y)

            features_image.append(
                model_without_ddp.encode_image(x)
                # gather_tensors(model_without_ddp.encode_image(x)).cpu()
            )
            if num_captions_per_img > 1:
                B, N, C = y["input_ids"].shape
                y = dict(map(lambda kv: (kv[0], kv[1].reshape(B * N, C)), y.items()))
            features_text.append(model_without_ddp.encode_text(y))

        features_image = torch.cat(features_image)
        features_text = torch.cat(features_text)

        i2t_similarities = features_image @ features_text.t()

        i2t_ranks = []
        for i, sim in enumerate(i2t_similarities.cpu().numpy()):
            inds = np.argsort(sim)[::-1]
            for r, ind in enumerate(inds):
                if i * num_captions_per_img <= ind < (i + 1) * num_captions_per_img:
                    rank = r
                    break
            i2t_ranks.append(rank)

        rank = [1, 5, 10]
        i2t_accs = [sum([_ < r for _ in i2t_ranks]) / len(i2t_ranks) for r in rank]

        t2i_similarities = features_text @ features_image.t()

        t2i_ranks = []
        for i, sim in enumerate(t2i_similarities.cpu().numpy()):
            inds = np.argsort(sim)[::-1]
            for r, ind in enumerate(inds):
                if i // num_captions_per_img == ind:
                    rank = r
                    break
            t2i_ranks.append(rank)

        rank = [1, 5, 10]
        t2i_accs = [sum([_ < r for _ in t2i_ranks]) / len(t2i_ranks) for r in rank]

        logger.info(
            "=> I2T Retrieval: {:.4f} @ R1, {:.4f} @ R5, {:.4f} @ R10".format(
                i2t_accs[0], i2t_accs[1], i2t_accs[2]
            )
        )
        logger.info(
            "=> T2I Retrieval: {:.4f} @ R1, {:.4f} @ R5, {:.4f} @ R10".format(
                t2i_accs[0], t2i_accs[1], i2t_accs[2]
            )
        )

        scores = {
            "i2t@R1": i2t_accs[0] * 100,
            "t2i@R1": t2i_accs[0] * 100,
            "mR": (sum(i2t_accs) + sum(t2i_accs))
            / (len(i2t_accs) + len(t2i_accs))
            * 100,
        }

        best_score = self.eval_best_scores.get("mR", 0)
        got_better_score = scores["mR"] > best_score

        if got_better_score:
            self.eval_best_scores = scores.copy()

        return scores, scores, True

    @torch.no_grad()
    def evaluate_vision_datasets_matching(self, trainer):

        if is_main_process():  # only evaluate on main process

            # model
            model = trainer.raw_modules["default"].model
            model_without_ddp = model.module if hasattr(model, "module") else model
            model_without_ddp.eval()

            # import vision_benchmark
            # from vision_benchmark.config import config
            # from vision_benchmark.config.default import _update_config_from_file
            # from vision_benchmark.commands.eval import alexandar_leaderboard
            # vision_benchmark_root = trainer.opt['VISION_BENCHMARK_MATCHING'].get('ROOT', 'Vision-Benchmark')

            # data
            # Vision-Benchmark/vision_benchmark/resources/datasets/bing-image-text-matching-english.yaml
            from torchvision import transforms
            from PIL import Image
            from vision_datasets import Usages
            from vision_datasets.pytorch import TorchDataset
            from vision_benchmark.common.constants import (
                get_dataset_hub,
                VISION_DATASET_STORAGE,
            )
            from vision_benchmark.evaluation.image_text_matching_evaluator import (
                collate_fn,
            )
            from vision_benchmark.common.utils import get_dataloader

            hub = get_dataset_hub()

            scores = {}
            for dataset_name in trainer.opt["VISION_BENCHMARK_MATCHING"]["DATASETS"]:
                dataset_info = hub.dataset_registry.get_dataset_info(dataset_name)
                assert dataset_info, "Dataset not exist."
                test_set = hub.create_manifest_dataset(
                    VISION_DATASET_STORAGE,
                    trainer.opt["VISION_BENCHMARK_MATCHING"].get(
                        "DATASET_DOWNLOAD_DIR", "tmp"
                    ),
                    dataset_name,
                    usage=Usages.TEST_PURPOSE,
                )

                transform = transforms.Compose(
                    [
                        transforms.Resize(
                            trainer.opt["IMAGE_ENCODER"]["IMAGE_SIZE"],
                            interpolation=Image.BICUBIC,
                        ),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=trainer.opt["IMAGE_ENCODER"]["IMAGE_MEAN"],
                            std=trainer.opt["IMAGE_ENCODER"]["IMAGE_STD"],
                        ),
                    ]
                )

                test_dataloader = get_dataloader(
                    TorchDataset(test_set, transform=transform), collate_fn
                )

                # translation
                if trainer.opt["VISION_BENCHMARK_MATCHING"].get("TRANSLATION", False):
                    translation_cache_file = trainer.opt[
                        "VISION_BENCHMARK_MATCHING"
                    ].get("TRANSLATION_CACHE_FILE", "/tmp/translation_cache.txt")
                    os.makedirs(os.path.dirname(translation_cache_file), exist_ok=True)
                    if os.path.exists(translation_cache_file):
                        with open(translation_cache_file, "r") as file:
                            translations = {
                                line.split("\t")[0]: line.split("\t")[1]
                                for line in file.read().splitlines()
                            }
                    else:
                        translations = {}
                    logger.info(f"Current translations: {len(translations.keys())}")

                # inference
                features_image = []
                features_text = []
                targets = []
                predictions = []
                for i, batch in enumerate(test_dataloader):
                    x, y = batch[:2]  # x: image, B x 3 x 224 x 224
                    texts = [
                        [item[0] for item in image_level_ann][0]
                        for image_level_ann in y
                    ]  # raw texts, 64 x 1 str
                    # num_texts = sum([len(_) for _ in texts])
                    # num_images = len(y)
                    # if num_texts != num_images:
                    #     print(texts)
                    # assert num_texts == num_images, f"Only support 1 image - 1 text,
                    # we have {num_texts} text and {num_images} images"
                    # texts = [_[0] for _ in texts]
                    is_match = [
                        item[1] for image_level_ann in y for item in image_level_ann
                    ]  # 1, 0, 1, 1, xxx

                    if trainer.opt["VISION_BENCHMARK_MATCHING"].get(
                        "TRANSLATION", False
                    ):
                        for ti in range(len(texts)):
                            if texts[ti] not in translations:
                                try:
                                    translations[texts[ti]] = translate(
                                        texts[ti],
                                        trainer.opt["VISION_BENCHMARK_MATCHING"][
                                            "TRANSLATION_KEY"
                                        ],
                                    )
                                    texts[ti] = translations[
                                        texts[ti]
                                    ]  # replace with en
                                except Exception:
                                    logger.info(
                                        f"{texts[ti]} is not translated, need to restart"
                                    )
                            else:
                                texts[ti] = translations[texts[ti]]  # replace with en

                    tokens = model.tokenizer(
                        texts,
                        padding="max_length",
                        truncation=True,
                        max_length=trainer.opt["LANG_ENCODER"]["CONTEXT_LENGTH"],
                        return_tensors="pt",
                    )

                    tokens["input_ids"].squeeze_()
                    tokens["attention_mask"].squeeze_()

                    x = x.cuda(non_blocking=True)
                    tokens = dict(
                        map(
                            lambda kv: (kv[0], kv[1].cuda(non_blocking=True)),
                            tokens.items(),
                        )
                    )

                    if model_without_ddp.dtype is torch.float16:
                        # in FP16 mode, DeepSpeed casts the model to FP16,
                        # so the input needs to be manually casted to FP16
                        x = cast_batch_to_half(x)
                        tokens = cast_batch_to_half(tokens)
                    elif model_without_ddp.dtype is torch.bfloat16:
                        # in FP16 mode, DeepSpeed casts the model to FP16,
                        # so the input needs to be manually casted to FP16
                        x = cast_batch_to_bf16(x)
                        tokens = cast_batch_to_bf16(tokens)

                    features_image.append(model_without_ddp.encode_image(x))
                    features_text.append(model_without_ddp.encode_text(tokens))
                    targets.extend(is_match)

                features_image = torch.cat(features_image)
                features_text = torch.cat(features_text)
                predictions.extend(
                    torch.nn.functional.cosine_similarity(
                        features_image, features_text, dim=1, eps=1e-08
                    )
                    .cpu()
                    .tolist()
                )

                # evaluate
                from vision_benchmark.evaluation.metric import (
                    get_vision_evaluation_metrics,
                )

                metric_name = trainer.opt["VISION_BENCHMARK_MATCHING"].get(
                    "METRIC", "roc_auc"
                )
                evaluator = get_vision_evaluation_metrics(metric_name)
                evaluator.add_predictions(predictions, targets)
                result = evaluator.get_report()  # {'roc_auc': 0.7141775506341094}
                for k, v in result.items():
                    scores[f"{dataset_name}_{k}"] = v

                if trainer.opt["VISION_BENCHMARK_MATCHING"].get("TRANSLATION", False):
                    translation_cache_file = trainer.opt[
                        "VISION_BENCHMARK_MATCHING"
                    ].get("TRANSLATION_CACHE_FILE", "/tmp/translation_cache.txt")
                    with open(translation_cache_file, "w") as file:
                        for k, v in translations.items():
                            file.write(f"{k}\t{v}\n")

            return scores, scores, False

    # START STATIC EVAL
    # =====================

    def get_batch_generator_knnshot(
        self,
        trainer: MainzTrainer,
        dataset: str,
        is_evaluation: bool,
        knnconfkey="KNNSHOT_EVAL_DATASET",
    ) -> Union[DataLoader, iterators.CheckpointableIterator]:
        """
        Get a batch generator from the task for "train", "dev", or "test" set.
        Make sure to use 'world_size' and 'rank' info in opt when preparing batch generator
        for distributed training.

        Args:
            trainer (MainzTrainer): trainer object
            dataset (str): "evaluation dataset"
            is_evaluation (bool): whether the batch generator is for evaluation or training

        Returns:
            Iterable: an iterable of class `DataLoader` that yields batches
        """
        distributed = self._opt["world_size"] > 1

        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        tokenizer = model_without_ddp.tokenizer

        dataloader = self.get_knnshot_eval_generator(
            distributed, knnconfkey, tokenizer=tokenizer
        )
        logger.info(f"num of val samples: {len(dataloader.dataset)}")

        return dataloader

    def get_knnshot_eval_generator(
        self, distributed, knnconfkey="KNNSHOT_EVAL_DATASET", tokenizer=None
    ):
        eval_dataset = self._opt[knnconfkey]
        data_format = eval_dataset.get("FORMAT", "jpg")

        transforms = build_transforms(self._opt, False)
        if data_format == "jpg":
            dataset = torchvision.datasets.ImageFolder(
                os.path.join(eval_dataset["ROOT"], "val"), transform=transforms
            )
        elif data_format == "vision-datasets":
            import pathlib
            from vision_datasets import DatasetHub, Usages
            from ..ImageDataLoader.vision_dataset import MultiClassTorchDatasetWrapper

            dataset_name = eval_dataset["SPLIT"]
            manifest_dataset = DatasetHub(
                pathlib.Path(eval_dataset["DATA_REG_JSON_PATH"]).read_text()
            ).create_manifest_dataset(
                container_sas=eval_dataset["BLOB_CONTAINER"],
                local_dir=eval_dataset["ROOT"],
                name=dataset_name,
                usage=Usages.TEST_PURPOSE,
            )
            dataset = MultiClassTorchDatasetWrapper(manifest_dataset, transforms)
        elif data_format == "zip":
            dataset = ZipData(
                path=eval_dataset["ZIP_FILE"],
                map_file=eval_dataset["ZIP_MAP_FILE"],
                transform=transforms,
            )
        # NCFC Support TSV file eval data for knn_shot
        elif data_format == "tsv":
            eval_image_tsv = eval_dataset["EVAL_IMAGE_TSV"]
            eval_text_tsv = eval_dataset["EVAL_TEXT_TSV"]

            dataset = TSVImageTextDatasetV2(
                eval_image_tsv,
                eval_text_tsv,
                transform=transforms,
                tokenize=tokenizer,
                context_length=self._opt["LANG_ENCODER"]["CONTEXT_LENGTH"],
                num_captions=1,
                text_format="json",
                is_train=False,
            )

        else:
            logger.error(f"Unknown evaluation data format: {data_format}")
            raise ValueError(f"Unknown evaluation data format: {data_format}")

        sampler = (
            torch.utils.data.distributed.DistributedSampler(dataset, shuffle=False)
            if distributed
            else None
        )
        data_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=self._opt["TEST"]["BATCH_SIZE_PER_GPU"],
            shuffle=False,
            num_workers=self._opt["WORKERS"],
            pin_memory=self._opt["PIN_MEMORY"],
            sampler=sampler,
            drop_last=False,
        )

        return data_loader

    @staticmethod
    @torch.no_grad()
    def knnshot_classifier(
        cfg,
        model,
        tokenizer=None,
        knnconfkey="KNNSHOT_EVAL_DATASET",
        embedding=True,
        hflip=False,
    ):

        transforms = build_transforms(cfg, False)
        num_captions = 1
        # tokenobj = build_tokenizer(cfg['LANG_ENCODER'])

        tokenobj = model.tokenizer

        text_format = cfg[knnconfkey].get("TEXT_FORMAT", "json")
        batch_size_per_gpu = cfg["TEST"]["BATCH_SIZE_PER_GPU"]
        metas = []
        cfg_data = cfg[knnconfkey]
        if "CLASSIFICATION_SETS" in cfg_data and "NUM_CLASSES" in cfg_data:
            for source, num_classes in zip(
                cfg_data["CLASSIFICATION_SETS"], cfg_data["NUM_CLASSES"]
            ):
                metas.append(
                    TSVMeta(
                        source=source, num_classes=num_classes, task="classification"
                    )
                )
        dataset = TSVImageTextDatasetV2(
            cfg[knnconfkey]["IMAGE_TSV"],
            cfg[knnconfkey]["TEXT_TSV"],
            transform=transforms,
            tokenize=tokenobj,
            context_length=cfg["LANG_ENCODER"]["CONTEXT_LENGTH"],
            num_captions=num_captions,
            text_format=text_format,
            is_train=False,
            sas_token_path=None,
            metas=metas,
        )

        data_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size_per_gpu,
            shuffle=False,
            num_workers=1,
            pin_memory=False,
            sampler=None,
            drop_last=False,
        )

        knnshot_weights = []
        knnshot_set = {}
        knnshot_lab = {}

        import sys

        minlabel = sys.maxsize
        maxlabel = -1

        ind = 0
        for i, (x, y, target, *rest) in enumerate(data_loader):
            x = x.cuda(non_blocking=True)
            if embedding:

                if model.dtype is torch.float16:
                    x = cast_batch_to_half(x)

                class_embedding = model.encode_image(x)

                # test time augmentation
                if hflip:
                    xf = torch.flip(x, [3]).cuda(non_blocking=True)
                    if model.dtype is torch.float16:
                        xf = cast_batch_to_half(xf)
                    features_image_f = model.encode_image(xf)
                    class_embedding = class_embedding / 2.0 + features_image_f / 2.0

            # save vectors in order
            for j in range(len(target)):
                if embedding:
                    knnshot_set[ind + j] = class_embedding[j]
                knnshot_lab[ind + j] = target[j]

                if target[j] < minlabel:
                    minlabel = target[j]

                if target[j] > maxlabel:
                    maxlabel = target[j]

            ind += len(target)

        # re-order vectors, assume one per category
        # for i in knnshot_set.keys():
        #    knnshot_weights.append(knnshot_set[i])
        knnshot_labels = list(knnshot_lab.values())
        if embedding:
            knnshot_weights = list(knnshot_set.values())
            knnshot_weights_ret = torch.stack(knnshot_weights, dim=1).cuda()
        else:
            knnshot_weights_ret = None

        return knnshot_weights_ret, knnshot_labels, minlabel, maxlabel

    def balancedAccTopN(self, gt, logits, n):
        retval = 0.0

        hits = {}
        total = {}

        pred_sort = torch.argsort(torch.from_numpy(logits), dim=1, descending=True)

        for i in range(gt.shape[0]):
            if gt[i] in total:
                total[gt[i]] += 1
            else:
                total[gt[i]] = 1
                hits[gt[i]] = 0

            if gt[i] in pred_sort[i, 0:n]:
                hits[gt[i]] += 1

        count = 0
        for k in total.keys():
            retval += hits[k] / total[k]
            count += 1

        return retval / count

    def rescaleLogits(self, logits, rescale=False, cweights_file=None):
        from os.path import exists

        if (cweights_file is None) or (rescale is False) or (not exists(cweights_file)):
            return logits

        else:
            cweights = torch.zeros((logits.shape[1])) + 1
            cwf = np.loadtxt(cweights_file)
            cweights = cweights * cwf
            cweights = cweights.unsqueeze(0)

            for i in range(logits.shape[0]):
                for j in range(logits.shape[1]):
                    logits[i, j] = logits[i, j] * cweights[0, j]
                logits[i, :] = logits[i, :] / torch.norm(logits[i, :], p=1)

        return logits

    # Convert logits from KNN similarity to label prediction logits
    def reformLogits(
        self,
        logits,
        knnshot_labels,
        k=10,
        cweights_file=None,
        numlabels=256,
        minlabel=0,
        weighted_voting=True,
    ):
        # maxlabel = int(max(knnshot_labels))
        # minlabel = int(min(knnshot_labels))
        # numlabels = maxlabel-minlabel+1

        retval = torch.zeros((logits.shape[0], numlabels)).cuda(
            non_blocking=True
        )  # - 1.0

        cweights = torch.zeros((numlabels)) + 1

        if cweights_file is not None:
            from os.path import exists

            if exists(cweights_file):
                cwf = np.loadtxt(cweights_file)

                # concatenate if we loaded more weights than used
                cwf = cwf[0:numlabels]
                cweights = cweights * cwf

        # find the sorting by index
        logits_sort_ind = torch.argsort(logits, dim=1, descending=True)

        for i in range(retval.shape[0]):
            for j in range(k):
                k_ind = logits_sort_ind[i, j]
                k_label = knnshot_labels[k_ind] - minlabel

                if weighted_voting:
                    vote = logits[i, k_ind]
                else:
                    vote = 1.0

                retval[i, k_label] += vote * cweights[k_label]

            retval[i, :] = retval[i, :] / torch.norm(retval[i, :], p=1)

        return retval

    def findBestF1Score(self, preds, gt, thr=None, weighted=0.0):

        best_f1 = 0
        best_thr = 0

        if thr is None:
            preds_sort = np.argsort(preds)

            for item in preds_sort:
                cthr = preds[item]
                p = (preds >= cthr).astype(int)
                cf1 = sklearn.metrics.f1_score(gt, p)

                if cf1 > best_f1:
                    best_f1 = cf1
                    best_thr = cthr
        else:
            p = (preds >= thr).astype(int)
            best_thr = thr
            best_f1 = sklearn.metrics.f1_score(gt, p)

        if weighted > 0.0:

            ta = best_thr - weighted
            pa = (preds >= ta).astype(int)
            fa = sklearn.metrics.f1_score(gt, pa)

            tb = best_thr + weighted
            pb = (preds >= tb).astype(int)
            fb = sklearn.metrics.f1_score(gt, pb)

            tw = (ta * fa + tb * fb + best_thr * best_f1) / (fa + fb + best_f1)

            best_thr = tw

        return best_f1, best_thr

    # This is the primary evaluation function for all search/classification benchmarks
    @torch.no_grad()
    def evaluate_static_search_classification_regression(
        self,
        cfg,
        trainer: MainzTrainer,
        dataset: str,
        save_folder,
        label="",
        knnconfkey="KNNSHOT_EVAL_DATASET",
        zeroshot_mode=0,
        trackmetricbestscore=None,
    ) -> Tuple[Dict, Dict[str, float], bool]:
        model = trainer.raw_modules["default"].model
        model_without_ddp = model.module if hasattr(model, "module") else model
        model_without_ddp.eval()

        eval_batch_gen = self.get_batch_generator_knnshot(
            trainer, dataset, is_evaluation=True, knnconfkey=knnconfkey
        )

        # test time augmentation
        hflip = cfg[knnconfkey].get("HFLIP", False)

        # The number of neighbors to use for classification
        knn = cfg[knnconfkey].get("KNN", 10)

        # The weights for each class
        cwf = cfg[knnconfkey].get("CWEIGHT_FILE", None)

        # Enable weighted voting for KNN classification
        weighted_voting = cfg[knnconfkey].get("WEIGHTED_VOTING", True)

        # compute BACC at top-N
        topn = cfg[knnconfkey].get("BACC_TOPN", 0)

        # optional binary metrics
        binary_metrics = cfg[knnconfkey].get("BINARY_METRICS", -1)

        # optional binary thresholds
        thresholds = cfg[knnconfkey].get("THRESHOLDS", None)

        # fit threshold around a window of the max
        tw = cfg[knnconfkey].get("THRESHOLD_WINDOW", 0.0)

        # The data samples for KNN
        # =================
        # Create a "KNN shot" classifier. This returns image embeddings and their labels
        # for later scoring in a KNN process.
        #
        # if this function is to run in zero-shot mode only, do not extract the embeddings
        # for the data. rather, just collect the label statistics.
        knnshot_weights, knnshot_labels, minlabel, maxlabel = self.knnshot_classifier(
            cfg,
            model_without_ddp,
            knnconfkey=knnconfkey,
            embedding=(zeroshot_mode < 2),
            hflip=hflip,
        )

        # Collect the labels of the dataset
        classnames = []
        with open(cfg[knnconfkey]["LABEL_FILE"], "r") as f:
            for la in f:
                classnames.append(la.strip())

        # Create the zero-shot classifier if this is to be used in this evaluation.
        logging.info("FIXED EVAL ZEROSHOT MODE: " + str(zeroshot_mode))
        if zeroshot_mode > 0:
            templates = []

            if cfg[knnconfkey].get("TEMPLATES", None):
                with open(cfg[knnconfkey]["TEMPLATES"], "r") as f:
                    for la in f:
                        templates.append(la.strip())
            else:
                templates = IMAGENET_DEFAULT_TEMPLATES

            zeroshot_weights = self.zeroshot_classifier(
                classnames,
                templates,
                model_without_ddp,
                max_length=self._opt["LANG_ENCODER"].get("CONTEXT_LENGTH", 77),
            )

        # GPU AGGREGATION DATA STRUCTURES
        # ==================
        datalen = len(eval_batch_gen.dataset)
        ws = self._opt["world_size"]
        import math

        gpu_job_size = math.ceil(datalen / ws)

        if cfg[knnconfkey].get("REGRESSION_EVAL", False):
            maxlabel = len(classnames) - 1  # int(max(knnshot_labels))
            minlabel = 0  # int(min(knnshot_labels))
            total_labels = len(classnames)  # maxlabel - minlabel + 1
        else:
            maxlabel = int(max(knnshot_labels))
            minlabel = int(min(knnshot_labels))
            total_labels = maxlabel - minlabel + 1

        localagg_logits = (
            torch.zeros((gpu_job_size, total_labels))
            .type(torch.float16)
            .cuda(non_blocking=True)
        )  # to(self._opt['device'])
        localagg_labels = (
            torch.zeros((gpu_job_size, 1)).type(torch.float16).cuda(non_blocking=True)
        )
        # ==================

        import time

        inference_time = 0
        t0 = time.time()
        n_samples = 0
        sm = torch.nn.Softmax(dim=1)

        for i, (batch) in enumerate(eval_batch_gen):

            # Support both ZIP and TSV file eval data for knn_shot
            if len(batch) == 2:
                x, y = batch
            else:
                x, tokens, y = batch

            x = x.cuda(non_blocking=True)
            y = y.cuda(non_blocking=True)
            if model_without_ddp.dtype is torch.float16:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                x = cast_batch_to_half(x)
                y = cast_batch_to_half(y)
            t1 = time.time()
            features_image = model_without_ddp.encode_image(x)

            # test time augmentation
            if hflip:
                xf = torch.flip(x, [3]).cuda(non_blocking=True)
                if model_without_ddp.dtype is torch.float16:
                    xf = cast_batch_to_half(xf)
                features_image_f = model_without_ddp.encode_image(xf)

            # Search ("KNN-SHOT") Mode
            if zeroshot_mode < 2:
                logits = sm(100.0 * features_image @ knnshot_weights)

                # test time augmentation
                if hflip:
                    logits_f = sm(100.0 * features_image_f @ knnshot_weights)
                    logits = logits * 0.5
                    logits += logits_f * 0.5

                # knn logic -- the current logits represent all the samples.
                # we must convert from sample logits to class logits.
                logits = self.reformLogits(
                    logits,
                    knnshot_labels,
                    knn,
                    cwf,
                    numlabels=total_labels,
                    minlabel=minlabel,
                    weighted_voting=weighted_voting,
                )

            # Classfication ("ZERO-SHOT", or "Text Search") Mode
            if zeroshot_mode > 0:
                logits_zs = 100.0 * features_image @ zeroshot_weights

                # test time augmentation
                if hflip:
                    logits_zs_f = 100.0 * features_image_f @ zeroshot_weights
                    logits_zs = logits_zs * 0.5
                    logits_zs += logits_zs_f * 0.5

                if zeroshot_mode == 1:
                    # mix the two predictions
                    logits = (
                        logits_zs * cfg[knnconfkey].get("ZS_WEIGHT", 1.0) + logits
                    ) / (cfg[knnconfkey].get("ZS_WEIGHT", 1.0) + 1.0)
                else:
                    logits = logits_zs

                # optional rescaling of logits -- not used currently
                logits = self.rescaleLogits(
                    logits, cfg[knnconfkey].get("ZS_RESCALE", False), cwf
                )

            # GPU AGGREGATION DATA STRUCTURE
            # ================================
            localagg_logits[n_samples: (n_samples + x.size(0)), :] = logits.squeeze()
            localagg_labels[n_samples: (n_samples + x.size(0)), 0] = (
                y.squeeze() - minlabel
            )
            # ================================

            t2 = time.time()
            inference_time += t2 - t1
            n_samples += x.size(0)

        logger.info(
            f"""KNN Total evaluation time  {time.time() - t0} over
            {n_samples}, model inference time {inference_time / n_samples * 1000} ms/image."""
        )

        # GPU AGGREGATION
        # ===============
        localagg = (
            torch.cat((localagg_labels, localagg_logits), dim=1)
            .type(torch.float16)
            .cuda(non_blocking=True)
        )  # to(self._opt['device'])

        if self._opt["world_size"] > 1:
            ga_list = [
                torch.zeros(
                    (gpu_job_size, localagg.shape[1]),
                    device=self._opt["device"],
                    dtype=torch.float16,
                )
                for _ in range(ws)
            ]
            torch.distributed.all_gather(ga_list, localagg)
            globalagg = torch.cat(ga_list, 0)

        else:
            globalagg = localagg
        # ===============

        globalagg_numpy = globalagg.cpu().numpy()

        globalagg_numpy_logits = globalagg_numpy[:, 1:]
        globalagg_numpy_labels = globalagg_numpy[:, 0].astype(int)

        scores = {}

        # REGRESSION EVAL TASK FROM KNN
        if cfg[knnconfkey].get("REGRESSION_EVAL", False):

            # These are not currently used and are removed to keep the logs clean
            # l1 = np.mean(globalagg_numpy_labels - np.argmax(globalagg_numpy_logits, axis=1))
            # std = np.std(globalagg_numpy_labels - np.argmax(globalagg_numpy_logits, axis=1))
            # l2 = np.mean((globalagg_numpy_labels - np.argmax(globalagg_numpy_logits, axis=1))**2)
            # scores.update({knnconfkey + '_l1_avg': l1})
            # scores.update({knnconfkey + '_l1_std': std})
            # scores.update({knnconfkey + '_l2_sum': l2})

            l1abs = np.mean(
                np.abs(
                    globalagg_numpy_labels - np.argmax(globalagg_numpy_logits, axis=1)
                )
            )
            scores.update({knnconfkey + "_l1_abs_avg": l1abs})

            rk = cfg[knnconfkey].get("REGRESS_K", 3)

            weightedvals = np.zeros(globalagg_numpy_logits.shape[0])
            wsort = np.argsort(globalagg_numpy_logits, axis=1)
            for i in range(globalagg_numpy_logits.shape[0]):
                rowscale = 0
                for j in range(1, rk + 1):
                    # weight each of the top "rk" predictions by their logit similarity scores
                    weightedvals[i] += (
                        globalagg_numpy_logits[i, wsort[i, -j]] * wsort[i, -j]
                    )
                    rowscale += globalagg_numpy_logits[i, wsort[i, -j]]

                # normalize by the sum of the logit similarity scores
                weightedvals[i] = weightedvals[i] / rowscale
            # l1w = np.mean(globalagg_numpy_labels - np.mean(weightedvals, axis=1))
            l1w = np.mean(np.abs(globalagg_numpy_labels - weightedvals))
            scores.update({knnconfkey + "_l1_w_avg": l1w})

        # CLASSIFICATION EVAL TASK FROM KNN or ZEROSHOT/TEXT
        else:

            auc = {}
            ap = {}

            # vinbrain binary metrics
            sens = {}
            spec = {}
            f1 = {}
            best_f1 = {}
            best_thr = {}

            bacc = sklearn.metrics.balanced_accuracy_score(
                globalagg_numpy_labels, np.argmax(globalagg_numpy_logits, axis=1)
            )
            acc = sklearn.metrics.accuracy_score(
                globalagg_numpy_labels, np.argmax(globalagg_numpy_logits, axis=1)
            )

            if topn > 0:
                bacc_topn = self.balancedAccTopN(
                    globalagg_numpy_labels, globalagg_numpy_logits, topn
                )
                acc_topn = sklearn.metrics.top_k_accuracy_score(
                    globalagg_numpy_labels,
                    globalagg_numpy_logits,
                    k=topn,
                    labels=list(range(total_labels)),
                )
                scores.update({knnconfkey + "_bacc_top" + str(topn): bacc_topn})
                scores.update({knnconfkey + "_acc_top" + str(topn): acc_topn})

            for i in range(globalagg_numpy_logits.shape[1]):
                try:
                    perf_prefix = (
                        "CONCEPT PERFORMANCE, "
                        + knnconfkey
                        + ", "
                        + classnames[i]
                        + ", "
                    )
                    auc[i] = sklearn.metrics.roc_auc_score(
                        (globalagg_numpy_labels == i), globalagg_numpy_logits[:, i]
                    )
                    ap[i] = sklearn.metrics.average_precision_score(
                        (globalagg_numpy_labels == i), globalagg_numpy_logits[:, i]
                    )
                    logger.info(perf_prefix + "AUC " + str(i) + " = " + str(auc[i]))
                    logger.info(perf_prefix + "AP " + str(i) + " = " + str(ap[i]))

                    fpr, tpr, thresholds = sklearn.metrics.roc_curve(
                        (globalagg_numpy_labels == i), globalagg_numpy_logits[:, i]
                    )

                    for j in range(len(fpr)):
                        logger.info(
                            perf_prefix
                            + "ROC THR , FPR , TPR "
                            + str(i)
                            + " = "
                            + str(thresholds[j])
                            + ","
                            + str(fpr[j])
                            + ","
                            + str(tpr[j])
                        )

                    # optional binary metrics
                    if binary_metrics >= 0:
                        pred_labels = (
                            np.argmax(globalagg_numpy_logits, axis=1) == i
                        ).astype(int)
                        gt = globalagg_numpy_labels == i
                        f1[i] = sklearn.metrics.f1_score(gt, pred_labels)

                        bthr = None
                        if thresholds is not None:
                            bthr = thresholds[i]

                        c_best_f1, c_best_thr = self.findBestF1Score(
                            np.squeeze(globalagg_numpy_logits[:, i]), gt, bthr, tw
                        )
                        best_f1[i] = c_best_f1
                        best_thr[i] = c_best_thr

                        sensitivity = sklearn.metrics.recall_score(
                            gt, pred_labels
                        )  # np.mean(pred_labels * gt.astype(int))
                        specificity = sklearn.metrics.recall_score(
                            gt, pred_labels, pos_label=0
                        )  # np.mean((1 - pred_labels) * (1 - gt.astype(int)))

                        sens[i] = sensitivity
                        spec[i] = specificity

                        logger.info(perf_prefix + "F1 " + str(i) + " = " + str(f1[i]))
                        logger.info(
                            perf_prefix + "SENS " + str(i) + " = " + str(sens[i])
                        )
                        logger.info(
                            perf_prefix + "SPEC " + str(i) + " = " + str(spec[i])
                        )
                        logger.info(
                            perf_prefix + "BEST_F1 " + str(i) + " = " + str(best_f1[i])
                        )
                        logger.info(
                            perf_prefix
                            + "BEST_THR "
                            + str(i)
                            + " = "
                            + str(best_thr[i])
                        )

                except Exception:
                    # This occurs if there is no GT values for the concept in the test set. Log it but skip.
                    logger.info("KNNSHOT_EVAL FAIL: Concept " + str(i) + " ...")

            mauc = np.mean(np.array(list(auc.values())))
            map = np.mean(np.array(list(ap.values())))

            scores.update(
                {
                    knnconfkey + "_bacc": bacc,
                    knnconfkey + "_mauc": mauc,
                    knnconfkey + "_map": map,
                    knnconfkey + "_acc": acc,
                }
            )

            got_better_score = False

            if trackmetricbestscore is not None:
                trackbest = knnconfkey + "_" + trackmetricbestscore

                best_score = self.eval_best_scores.get(trackbest, 0)
                got_better_score = scores[trackbest] > best_score

                if got_better_score:
                    self.eval_best_scores = scores.copy()

            if binary_metrics >= 0:
                macro_f1 = np.mean(np.array(list(f1.values())))
                best_macro_f1 = np.mean(np.array(list(best_f1.values())))
                scores.update(
                    {
                        knnconfkey
                        + "_sens_"
                        + str(binary_metrics): sens[binary_metrics],
                        knnconfkey
                        + "_spec_"
                        + str(binary_metrics): spec[binary_metrics],
                        knnconfkey + "_f1_" + str(binary_metrics): f1[binary_metrics],
                        knnconfkey + "_auc_" + str(binary_metrics): auc[binary_metrics],
                        knnconfkey + "_ap_" + str(binary_metrics): ap[binary_metrics],
                        knnconfkey + "_macrof1": macro_f1,
                        knnconfkey + "_bestmacrof1": best_macro_f1,
                    }
                )

                logger.info("KNNSHOT_EVAL: THRESHOLDS: " + str(best_thr))

        print("SCORES (" + knnconfkey + "):  " + str(scores))

        return scores, scores, got_better_score


# END STATIC EVAL
# =====================


# FROM HTTPS://GITHUB.COM/LUYUG/gRADcACHE


class RandContext:
    def __init__(self, *tensors):
        self.fwd_cpu_state = torch.get_rng_state()
        self.fwd_gpu_devices, self.fwd_gpu_states = get_device_states(*tensors)

    def __enter__(self):
        self._fork = torch.random.fork_rng(devices=self.fwd_gpu_devices, enabled=True)
        self._fork.__enter__()
        torch.set_rng_state(self.fwd_cpu_state)
        set_device_states(self.fwd_gpu_devices, self.fwd_gpu_states)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fork.__exit__(exc_type, exc_val, exc_tb)
        self._fork = None


def get_input_tensors(model_input) -> List[Tensor]:
    """
    Recursively go through model input and grab all tensors, which are then used to record current device random
    states. This method will do its best to parse types of Tensor, tuple, list, dict and UserDict. Other types will
    be ignored unless self._get_input_tensors_strict is set to True, in which case an exception will be raised.
    :param model_input: input to model
    :return: all torch tensors in model_input
    """
    if isinstance(model_input, Tensor):
        return [model_input]
    elif isinstance(model_input, (list, tuple)):
        return sum((get_input_tensors(x) for x in model_input), [])
    elif isinstance(model_input, dict):
        return sum((get_input_tensors(x) for x in model_input.values()), [])
    else:
        return []

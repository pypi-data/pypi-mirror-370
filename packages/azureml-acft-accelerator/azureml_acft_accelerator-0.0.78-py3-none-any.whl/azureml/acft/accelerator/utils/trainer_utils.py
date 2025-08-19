# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains utilty functions for Training
"""
import json
import argparse
from typing import Optional, Dict, Any, Union
from pathlib import Path
import shutil
import inspect

import torch
from datasets.arrow_dataset import Dataset
from transformers.training_args import TrainingArguments
from transformers.training_args_seq2seq import Seq2SeqTrainingArguments
from transformers.trainer_seq2seq import Seq2SeqTrainer
from transformers.trainer import Trainer

from optimum.onnxruntime import ORTTrainer, ORTSeq2SeqTrainer, ORTTrainingArguments

from ..constants import (
    HfTrainerMethodsConstants,
    HfTrainerType,
    SaveFileConstants,
)
from ..utils.code_utils import get_model_custom_code_files, copy_code_files
from ..utils.license_utils import download_license_file

from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)


class TrainerMixin:
    """
    This is a mixin class that needs to used in conjunction with either of the below classes
        Trainer
        ORTTrainer
        Seq2SeqTrainer
        ORTSeq2SeqTrainer
    This class provides extra utility functions for trainer. Also it helps to customize some methods.
    """

    CUSTOM_FUNCTIONS = {}
    OPTIMIZATION_ARGS = {}
    IO_ARGS = {}

    def load_model_finetuned_weights(self, resume_from_checkpoint: str):
        """
        load finetuned weights of a model
        applies lora weights + deepspeed init is handled internally
        """
        self.state.best_model_checkpoint = resume_from_checkpoint
        self._load_best_model()
        self.state.best_model_checkpoint = None

    def _get_train_sampler(self, train_dataset: Optional[Dataset] = None) -> Optional[torch.utils.data.Sampler]:
        if train_dataset is None:
            train_dataset = self.train_dataset
        if train_dataset is None:
            return None
        if HfTrainerMethodsConstants.AZUREML_TRAIN_SAMPLER in self.__class__.CUSTOM_FUNCTIONS:
            custom_train_sampler_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_TRAIN_SAMPLER]
            logger.info(f"Using custom train sampler: {custom_train_sampler_func}")
            return custom_train_sampler_func(train_dataset, self.args.world_size)
        else:
            logger.info("Calling the default train sampler")
            return super(TrainerMixin, self)._get_train_sampler()

    def _get_eval_sampler(self, eval_dataset: Dataset) -> Optional[torch.utils.data.Sampler]:
        if HfTrainerMethodsConstants.AZUREML_EVAL_SAMPLER in self.__class__.CUSTOM_FUNCTIONS:
            custom_eval_sampler_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_EVAL_SAMPLER]
            logger.info(f"Using custom eval sampler: {custom_eval_sampler_func}")
            return custom_eval_sampler_func(eval_dataset, self.args.world_size)
        else:
            logger.info("Calling the default eval sampler")
            return super()._get_eval_sampler(eval_dataset)

    def create_optimizer(self):
        if HfTrainerMethodsConstants.AZUREML_OPTIMIZER in self.__class__.CUSTOM_FUNCTIONS:
            create_optimizer_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_OPTIMIZER]
            logger.info(f"Using custom optimizer: {create_optimizer_func}")
            self.optimizer = create_optimizer_func(self.model, learning_rate=self.args.learning_rate)
        else:
            logger.info("Calling the default optimizer")
            super().create_optimizer()

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        if HfTrainerMethodsConstants.AZUREML_COMPUTE_LOSS in self.__class__.CUSTOM_FUNCTIONS:
            compute_loss_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_COMPUTE_LOSS]
            logger.info(f"Using custom loss func: {compute_loss_func}")
            if "num_items_in_batch" in list(inspect.signature(compute_loss_func).parameters.keys()):
                # new argument in transformers>=4.46.0
                return compute_loss_func(model, inputs, return_outputs=return_outputs, num_items_in_batch=num_items_in_batch)
            else:
                # backward compatibility for transformers<4.46.0
                return compute_loss_func(model, inputs, return_outputs=return_outputs)
        else:
            if "num_items_in_batch" in list(inspect.signature(super().compute_loss).parameters.keys()):
                # new argument in transformers>=4.46.0
                return super().compute_loss(model, inputs, return_outputs=return_outputs, num_items_in_batch=num_items_in_batch)
            else:
                # backward compatibility for transformers<4.46.0
                return super().compute_loss(model, inputs, return_outputs=return_outputs)

    def save_model(self, output_dir: Optional[str] = None, _internal_call: bool = False):
        """
        Will save the model, so you can reload it using `from_pretrained()`.
        Will only save from the main process.
        """

        # HACK setting `use_cache=True` while saving the model
        # The saved model is used in downstream model prediction component.
        # Adding this hacks helps to speed up the model.generate().
        self.model.config.use_cache = True

        super().save_model(output_dir, _internal_call)

        # HACK resetting `use_cache=False` for continuing the finetuning
        # Setting the flag to False will help with large model finetuning.
        self.model.config.use_cache = False

        # save additional files required by acft model
        self.save_acft_pytorch_model_files(output_dir)

    def save_acft_pytorch_model_files(self, output_dir):
        """Will save additional files required for acft pytorch model from base model."""

        # save files in the main process only
        # else checkpoit-{{step_number}} file is getting created before directory being created
        if self.args.should_save:
            logger.info("Saving additional pytorch model files")

            # check if root model has any custom code files and copy them to output model
            if hasattr(self.model.config, "auto_map"):
                logger.info("Saving code files to pytorch model")
                # Check if any code files are present in the model folder
                model_path = str(Path(
                    self.__class__.IO_ARGS["model_selector_output"],
                    self.__class__.OPTIMIZATION_ARGS["model_name"],
                ))
                py_code_files = get_model_custom_code_files(model_path, self.model)

                # copying the py files
                copy_code_files(py_code_files, [output_dir])

            # saving input model LICENSE file to output
            if self.__class__.OPTIMIZATION_ARGS["model_name"]:
                license_file_path = Path(
                    self.__class__.IO_ARGS["model_selector_output"],
                    self.__class__.OPTIMIZATION_ARGS["model_name"],
                    SaveFileConstants.LICENSE_SAVE_PATH
                )
                if license_file_path.is_file():
                    shutil.copy(str(license_file_path), output_dir)
                    logger.info("LICENSE file is copied to pytorch model folder")
                else:
                    download_license_file(
                        self.__class__.OPTIMIZATION_ARGS["model_name"],
                        output_dir,
                    )


class TrainerExtended(TrainerMixin, Trainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass


class Seq2SeqTrainerExtended(TrainerMixin, Seq2SeqTrainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass


class ORTTrainerExtended(TrainerMixin, ORTTrainer):
    """
    Subclassed Trainer class to customize behaviour. ORT is assumed to be pre-installed in the PTCA image
    """
    pass


class ORTSeq2SeqTrainerExtended(TrainerMixin, ORTSeq2SeqTrainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass


def identify_trainer_cls(trainer_type: str, apply_ort: bool):
    """
    Identify the trainer class and training arguments class
    """
    if trainer_type == HfTrainerType.SEQ2SEQ:
        return ORTSeq2SeqTrainerExtended if apply_ort else Seq2SeqTrainerExtended
    else:
        return ORTTrainerExtended if apply_ort else TrainerExtended


def identify_training_args_cls(trainer_type: str, apply_ort: bool):
    """
    Identify the trainer class and training arguments class
    """
    if trainer_type == HfTrainerType.SEQ2SEQ:
        return Seq2SeqTrainingArguments
    else:
        return ORTTrainingArguments if apply_ort else TrainingArguments


def get_deepspeed_dict(deepspeed_config: Union[Dict, str]) -> Dict:
    if isinstance(deepspeed_config, dict):
        # deepspeed can also be a dict which has already been loaded from deepspeed json file.
        # return it as is in such cases.
        return deepspeed_config
    with open(deepspeed_config) as fp:
        deepspeed_config = json.load(fp)
    return deepspeed_config


def resolve_conflicts_trainer_deepspeed_args(finetune_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    :param finetune_args: finetune component args loaded from component parameters
        If deepspeed is enabled, read the deepspeed config args and resolve conflicts with trainer_args
        NOTE deepspeed config parameters are given preference over component parameters
    """

    finetune_args_namespace = argparse.Namespace(**finetune_args)

    if finetune_args_namespace.deepspeed is not None:
        ds_dict = get_deepspeed_dict(finetune_args_namespace.deepspeed)

        # per_device_train_batch_size
        # deepspeed - train_batch_size can not be handled currently, needs to be checked by user only
        # TODO: replicate for eval batch size
        if hasattr(finetune_args_namespace, "per_device_train_batch_size"):
            per_device_train_batch_size = ds_dict.get("train_micro_batch_size_per_gpu", finetune_args_namespace.per_device_train_batch_size)
            if per_device_train_batch_size != "auto":
                setattr(finetune_args_namespace, "per_device_train_batch_size", per_device_train_batch_size)

        # gradient_accumulation_steps
        if hasattr(finetune_args_namespace, "gradient_accumulation_steps"):
            gradient_accumulation_steps = ds_dict.get("gradient_accumulation_steps", finetune_args_namespace.gradient_accumulation_steps)
            if gradient_accumulation_steps != "auto":
                setattr(finetune_args_namespace, "gradient_accumulation_steps", gradient_accumulation_steps)

        # train_batch_size - not implemented as calculated by HFTrainer

        # max_grad_norm
        if hasattr(finetune_args_namespace, "max_grad_norm"):
            max_grad_norm = ds_dict.get("gradient_clipping", finetune_args_namespace.max_grad_norm)
            if max_grad_norm != "auto":
                setattr(finetune_args_namespace, "max_grad_norm", max_grad_norm)

        # optimizer
        if "optimizer" in ds_dict and "params" in ds_dict["optimizer"]:
            # learning_rate
            if hasattr(finetune_args_namespace, "learning_rate"):
                learning_rate = ds_dict["optimizer"]["params"].get("lr", finetune_args_namespace.learning_rate)
                if learning_rate != "auto":
                    setattr(finetune_args_namespace, "learning_rate", learning_rate)
            # adam_betas
            if hasattr(finetune_args_namespace, "adam_beta1") and hasattr(finetune_args_namespace, "adam_beta2"):
                if "betas" in ds_dict["optimizer"]["params"] and ds_dict["optimizer"]["params"]["betas"] != "auto":
                    setattr(finetune_args_namespace, "adam_beta1", ds_dict["optimizer"]["params"]["betas"][0])
                    setattr(finetune_args_namespace, "adam_beta2", ds_dict["optimizer"]["params"]["betas"][1])
            # adam_epsilon
            if hasattr(finetune_args_namespace, "adam_epsilon"):
                adam_epsilon = ds_dict["optimizer"]["params"].get("eps", finetune_args_namespace.adam_epsilon)
                if adam_epsilon != "auto":
                    setattr(finetune_args_namespace, "adam_epsilon", adam_epsilon)
            # weight_decay
            if hasattr(finetune_args_namespace, "weight_decay"):
                weight_decay = ds_dict["optimizer"]["params"].get("weight_decay", finetune_args_namespace.weight_decay)
                if weight_decay != "auto":
                    setattr(finetune_args_namespace, "weight_decay", weight_decay)

        # scheduler
        if "scheduler" in ds_dict and "params" in ds_dict["scheduler"]:
            # learning_rate
            if hasattr(finetune_args_namespace, "learning_rate"):
                learning_rate = ds_dict["scheduler"]["params"].get("warmup_max_lr", finetune_args_namespace.learning_rate)
                if learning_rate != "auto":
                    setattr(finetune_args_namespace, "learning_rate", learning_rate)
            # warmup_steps
            if hasattr(finetune_args_namespace, "warmup_steps"):
                warmup_steps = ds_dict["scheduler"]["params"].get("warmup_num_steps", finetune_args_namespace.warmup_steps)
                if warmup_steps != "auto":
                    setattr(finetune_args_namespace, "warmup_steps", warmup_steps)
            # max_steps
            if hasattr(finetune_args_namespace, "max_steps"):
                max_steps = ds_dict["scheduler"]["params"].get("total_num_steps", finetune_args_namespace.max_steps)
                if max_steps != "auto":
                    setattr(finetune_args_namespace, "max_steps", max_steps)

        # fp-16
        if hasattr(finetune_args_namespace, "fp16"):
            fp16 = ds_dict.get("fp16", {}).get("enabled", finetune_args_namespace.fp16)
            if fp16 != "auto":
                setattr(finetune_args_namespace, "fp16", fp16)
        # fp16_full_eval, fp16_backend - not implemented by azmlft
        # fp16_backend is auto handled by HfTrainerDeepSpeedConfig and is always "amp" for azmlft
        setattr(finetune_args_namespace, "fp16_opt_level", "O1")      # default HFTrainer value
        fp16_opt_level = ds_dict.get("amp", {}).get("opt_level", finetune_args_namespace.fp16_opt_level)
        if fp16_opt_level != "auto":
            setattr(finetune_args_namespace, "fp16_opt_level", fp16_opt_level)

        # bf16
        if hasattr(finetune_args_namespace, "bf16"):
            bf16 = ds_dict.get("bf16", {}).get("enabled", finetune_args_namespace.bf16)
            if bf16 != "auto":
                setattr(finetune_args_namespace, "bf16", bf16)

        logger.info(
            f"Resolved conflicts between finetune_args_namespace and deepspeed config: {finetune_args_namespace}")

    else:
        setattr(finetune_args_namespace, "fp16_opt_level", "O1")  # default HFTrainer value

    return vars(finetune_args_namespace)


def is_nebula_enabled(deepspeed_config: Union[Dict, str]) -> bool:
    if not deepspeed_config:
        return False
    ds_dict = get_deepspeed_dict(deepspeed_config)
    nebula: Dict = ds_dict.get("nebula")
    return bool(nebula and nebula.get("enabled"))

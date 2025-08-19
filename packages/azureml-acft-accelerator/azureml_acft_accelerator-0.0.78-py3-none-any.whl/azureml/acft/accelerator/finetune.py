# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File Containing Functions for finetuning a pre trained model
"""

import os
import json
import time
import math
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Union, Optional
from pathlib import Path

from transformers import TrainerCallback
from transformers import PreTrainedTokenizerBase, PreTrainedModel
from transformers.trainer import Trainer
from transformers.trainer_seq2seq import Seq2SeqTrainer
from transformers.trainer_callback import EarlyStoppingCallback
from transformers.trainer_utils import IntervalStrategy
from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import Dataset as TorchDataset, IterableDataset as TorchIterableDataset

from datasets.arrow_dataset import Dataset as DatasetsDataset
from datasets.iterable_dataset import IterableDataset as DatasetsIterableDataset

from .constants import SaveFileConstants, AzuremlConstants
from .constants import _AzuremlOptimizationArgs, _AzuremlIOArgs, _AzuremlModelMetaArgs, HfTrainerType, LoraAlgo
from .lora_wrapper.peft_lora_wrapper import PeftLoraWrapper
from .lora_wrapper.lora_wrapper import LoraWrapper
from .utils.hf_argparser import HfArgumentParser
from .utils.callbacks import LoraPyTorchSaveCallback, FinetuneCallback, NebulaCallback, \
    ShouldSaveCheckpointOnEvaluate, ShouldSaveCheckpointOnSingularityPreemption

from .utils.trainer_utils import (
    identify_training_args_cls,
    identify_trainer_cls,
    resolve_conflicts_trainer_deepspeed_args,
    is_nebula_enabled,
)
from .utils.model_utils import add_lora_layers_to_model

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.callbacks import SaveExtraFilesToCheckpoints
from azureml.acft.common_components.utils.error_handling.swallow_all_exceptions_decorator import (
    swallow_all_exceptions
)


logger = get_logger_app(__name__)


class AzuremlFinetuneArgs:
    def __init__(
        self,
        finetune_args: Dict[str, Any],
        trainer_type: str = HfTrainerType.DEFAULT,
    ) -> None:

        # resolve deepspeed vs trainer parameters
        if finetune_args.get("deepspeed", None) is not None:
            finetune_args = resolve_conflicts_trainer_deepspeed_args(finetune_args)

        if trainer_type not in HfTrainerType.get_fields():
            raise Exception(f"Trainer type not supported. It should be one of {HfTrainerType.get_fields()}")
        self.trainer_type = trainer_type

        apply_ort = finetune_args.get("apply_ort", False)
        training_args_cls = identify_training_args_cls(trainer_type, apply_ort)
        logger.info(f"Identified training args class: {training_args_cls}")

        # Set this flag to enable training in CPU computes
        if not torch.cuda.is_available():
            finetune_args["xpu_backend"] = "mpi"
            finetune_args["no_cuda"] = True
            logger.warning(
                "CPU compute based training is in experimental stage. ONLY single process training works for now"
            )

        if not finetune_args.pop("save_checkpoints_to_output", True):
            finetune_args["output_dir"] = SaveFileConstants.ACFT_TRAINER_CHECKPOINTS_PATH
            Path(finetune_args["output_dir"]).mkdir(exist_ok=True, parents=True)
            logger.info("Using ACFT_TRAINER_CHECKPOINTS_PATH to save checkpoints")

        # parse the data into training args and optimzation args
        parser = HfArgumentParser([_AzuremlOptimizationArgs, _AzuremlIOArgs, _AzuremlModelMetaArgs, training_args_cls])
        (self.optimization_args, self.io_args, self.modelmeta_args, self.trainer_args), unused_args = parser.parse_dict(
            finetune_args,
            allow_extra_keys=True
        )

        self.__post_init__()

        logger.info(f"Optimization args: {self.optimization_args}")
        logger.info(f"IO args: {self.io_args}")
        logger.info(f"The following args are unused by the trainer - {unused_args}")
        logger.info(f"Trainer args: {self.trainer_args}")
        logger.info(f"ModelMeta args: {self.modelmeta_args}")

    def __post_init__(self):
        """Set some additional trainer args"""
        setattr(self.trainer_args, "report_to", [])
        # Loads the model at the end of training so that the best model will be saved in the end
        logger.warn("Enforcing load_best_model_at_end=True so that finetuning output in the end is the best model checkpoint and not the last checkpoint")
        setattr(self.trainer_args, "load_best_model_at_end", True)
        if self.optimization_args.apply_lora and self.optimization_args.lora_algo == LoraAlgo.AUTO:
            # force peft algorithm for lora in case of 4/8 bit or deepspeed stage-3 training
            if self._enable_peft():
                logger.info(
                    "Finetuning with quantization/deepspeed stage-3 is enabled with lora. "
                    "Forcing the lora algorithm to peft."
                )
                setattr(self.optimization_args, "lora_algo", LoraAlgo.PEFT)
            else:
                logger.info("Enabling custom lora")
                setattr(self.optimization_args, "lora_algo", LoraAlgo.CUSTOM)

    def _enable_peft(self) -> bool:
        """Force enable peft when quantization or stage3 is enabled with LoRA."""
        if (
            self.optimization_args.finetune_in_8bit or
            self.optimization_args.finetune_in_4bit or
            is_deepspeed_zero3_enabled()
        ):
            return True
        return False

    def save(self):
        if self.trainer_args.should_save:  # save only on rank-0
            # saving only optimization and io args here
            # trainer args will be save as part of :func trainer _save method
            optimization_args_save_path = os.path.join(self.io_args.pytorch_model_folder, SaveFileConstants.OPTIMIZATION_ARGS_SAVE_PATH)
            with open(optimization_args_save_path, 'w') as fp:
                json.dump(asdict(self.optimization_args), fp, indent=2)

            io_args_save_path = os.path.join(self.io_args.pytorch_model_folder, SaveFileConstants.IO_ARGS_SAVE_PATH)
            with open(io_args_save_path, 'w') as fp:
                json.dump(asdict(self.io_args), fp, indent=2)


class AzuremlDatasetArgs:
    def __init__(
        self,
        train_dataset: Union[TorchDataset, TorchIterableDataset, DatasetsDataset, DatasetsIterableDataset],
        validation_dataset: Union[TorchDataset, TorchIterableDataset, DatasetsDataset, DatasetsIterableDataset],
        data_collator: Optional[Callable],
    ):
        self.train_dataset = train_dataset
        self.validation_dataset = validation_dataset
        self.data_collator = data_collator


class AzuremlTrainer:
    """Azureml trainer class to train/finetune the model"""

    def __init__(
        self,
        finetune_args: AzuremlFinetuneArgs,
        dataset_args: AzuremlDatasetArgs,
        model: Union[nn.Module, PreTrainedModel],
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        metric_func: Optional[Callable] = None,
        preprocess_logits_for_metrics_callback: Optional[Callable] = None,
        custom_trainer_callbacks: Optional[List[TrainerCallback]] = None,
        custom_trainer_functions: Optional[Dict[str, Callable]] = None,
        new_initalized_layers: Optional[List[str]] = None,
        hf_trainer: Optional[Union[Trainer, Seq2SeqTrainer]] = None
    ):
        self.finetune_args = finetune_args
        self.optimization_args = finetune_args.optimization_args
        self.io_args = finetune_args.io_args
        self.trainer_args = finetune_args.trainer_args
        self.modelmeta_args = finetune_args.modelmeta_args
        self.trainer_cls = identify_trainer_cls(finetune_args.trainer_type, self.optimization_args.apply_ort)
        logger.info(f"Identified trainer class: {self.trainer_cls}")

        self.dataset_args = dataset_args
        self.custom_trainer_functions = custom_trainer_functions or {}
        self.custom_trainer_callbacks = custom_trainer_callbacks or []

        # TODO add validations for interfaces
        self.model = model
        self.new_initalized_layers = new_initalized_layers
        self.tokenizer = tokenizer
        self.metric_func = metric_func
        self.preprocess_logits_for_metrics_callback = preprocess_logits_for_metrics_callback

        self.__post_init__()

    def __post_init__(self):
        # TODO add validations for interfaces
        # set attributes to the trainer function
        setattr(self.trainer_cls, "CUSTOM_FUNCTIONS", self.custom_trainer_functions)
        setattr(self.trainer_cls, "OPTIMIZATION_ARGS", self.optimization_args.__dict__)
        setattr(self.trainer_cls, "IO_ARGS", self.io_args.__dict__)
        setattr(self.trainer_cls, "MODELMETA_ARGS", self.modelmeta_args.__dict__)

    @swallow_all_exceptions(time_delay=60)
    def train(self):
        """
        prepares necessary objects for finetuning and triggers finetuning and saves the best model
        """

        model, lora_wrapper_obj = self.model, None

        # Set leaf modules for MoE models in case of deepspeed stage 3.
        # This is to stop recursively setting hooks for modules in MoE models.
        if is_deepspeed_zero3_enabled() and self.optimization_args.leaf_modules_of_moe_models:
            from .utils.deepspeed_utils import set_z3_leaf_modules_for_moe_models
            set_z3_leaf_modules_for_moe_models(model, self.optimization_args.leaf_modules_of_moe_models)

        is_lora_weights_path_exist = False
        if self.optimization_args.model_name is not None:
            finetune_lora_weights_path = os.path.join(
                self.io_args.model_selector_output,
                self.optimization_args.model_name,
                AzuremlConstants.LORA_BASE_FOLDER, AzuremlConstants.LORA_WEIGHTS_NAME
            )
            is_lora_weights_path_exist = os.path.isfile(finetune_lora_weights_path)

        # TODO move the entire lora wrapping code to :func model_init or lora callback
        if self.optimization_args.apply_lora:
            if self.optimization_args.lora_algo == LoraAlgo.PEFT:
                peft_lora_wrapper = PeftLoraWrapper(
                    model=model,
                    model_name_or_path=os.path.join(
                        self.io_args.model_selector_output, self.optimization_args.model_name
                    ),
                    finetune_in_4bit=self.optimization_args.finetune_in_4bit,
                    finetune_in_8bit=self.optimization_args.finetune_in_8bit,
                    lora_alpha=self.optimization_args.lora_alpha,
                    lora_r=self.optimization_args.lora_r,
                    lora_dropout=self.optimization_args.lora_dropout,
                    newly_initialized_layers=self.new_initalized_layers,
                    peft_task_type=self.optimization_args.peft_task_type,
                    target_modules=self.optimization_args.lora_target_modules,
                    target_parameters=self.optimization_args.lora_target_parameters,
                )
                # not enabling gradient checkpointing as needs to be handled PeftLoraWrapper
                # TODO: use trainer_args.gradient_checkpointing at prepare_model_for_kbit_training
                if not (self.optimization_args.finetune_in_4bit or self.optimization_args.finetune_in_8bit) \
                        and self.trainer_args.gradient_checkpointing:
                    logger.info("Enabling gradient checkpointing for peft LoRA model")
                    peft_lora_wrapper.model.gradient_checkpointing_enable()
                peft_lora_wrapper.peft_model_init()
                lora_wrapper_obj = peft_lora_wrapper
                model = peft_lora_wrapper.model
            else:   # custom LoRA
                logger.info("Preparing lora model")
                model, lora_wrapper_obj = add_lora_layers_to_model(
                    model=model,
                    unmerge_weights=is_lora_weights_path_exist,
                    optimizer_args=self.optimization_args,
                    new_initialized_layers=self.new_initalized_layers
                )

        # commenting below code for now as Flash attention V1 implementation will be taken up later
        # if self.optimization_args.flash_attention_version == 1:
        #     # convert model to half precision (16 bit)
        #     logger.info("Converting model to 16 bit as using FlashAttention.")
        #     model.half()
        #     # convert model to bettertransformer
        #     model = model.to_bettertransformer()    # type: ignore
        #     logger.info("Model converted to bettertransformer")

        if (
            isinstance(self.dataset_args.train_dataset, (DatasetsDataset, TorchDataset)) and
            self.trainer_args.eval_strategy == IntervalStrategy.STEPS and
            self.optimization_args.evaluation_steps_interval > 0
        ):
            # resetting eval_steps only for fixed size datasets
            logger.info("Updating eval steps")
            # TODO Move this to post_init
            num_examples = len(self.dataset_args.train_dataset)  # type:ignore
            logger.info(f"number of trining examples: {num_examples}, world size: {self.trainer_args.world_size}")
            num_update_steps_per_epoch = num_examples // self.trainer_args.gradient_accumulation_steps
            num_update_steps_per_epoch = max(num_update_steps_per_epoch, 1)
            num_update_steps_per_epoch_per_world = max(num_update_steps_per_epoch // self.trainer_args.world_size, 1)
            mod_steps = int(
                math.floor(num_update_steps_per_epoch_per_world * self.optimization_args.evaluation_steps_interval))
            setattr(self.trainer_args, "eval_steps", mod_steps)
            setattr(self.trainer_args, "save_steps", mod_steps)
            # TODO Update evaluation_steps in scripts file to eval_steps
            logger.info(f"Updated evaluation_steps from {self.trainer_args.eval_steps} to {mod_steps}")

        # adding trainer callbacks
        trainer_callbacks = []
        trainer_callbacks.append(FinetuneCallback(
            log_metrics_at_root=self.optimization_args.log_metrics_at_root,
            set_log_prefix=self.optimization_args.set_log_prefix,
            model_name=self.optimization_args.model_name,
        ))
        trainer_callbacks.append(ShouldSaveCheckpointOnEvaluate())
        if self.optimization_args.apply_early_stopping:
            logger.info("Applying Early stopping as trainer callback")
            early_stopping = EarlyStoppingCallback(
                early_stopping_patience=self.optimization_args.early_stopping_patience,
                early_stopping_threshold=self.optimization_args.early_stopping_threshold,
            )
            trainer_callbacks.append(early_stopping)
        if is_nebula_enabled(self.trainer_args.deepspeed):
            logger.info("Applying Nebula as trainer callback")
            trainer_callbacks.append(NebulaCallback())
        # save extrafiles to checkpointfolders
        trainer_callbacks.append(SaveExtraFilesToCheckpoints(
            metadata=self.finetune_args.modelmeta_args.model_metadata,
            model_selector_output=self.finetune_args.io_args.model_selector_output,
            optimization_args = self.optimization_args,
            io_args=self.io_args,
        ))
        logger.info(f"Trainer callbacks: {trainer_callbacks}")

        self.hf_trainer = self.ft_with_trainer(
            model,
            trainer_callbacks=trainer_callbacks,
            lora_wrapper_obj=lora_wrapper_obj,
            load_lora_weights=is_lora_weights_path_exist,
        )

        # save model in case of lora disabled
        if not self.optimization_args.apply_lora:
            self.hf_trainer.save_model(self.io_args.pytorch_model_folder)

        # saving the args
        self.finetune_args.save()

        # Adding a barrier to wait for all the processes to finish
        if dist.is_initialized():
            logger.info("Waiting at barrier")
            dist.barrier()

    def ft_with_trainer(
        self,
        model: Union[nn.Module, PreTrainedModel],
        trainer_callbacks: List[TrainerCallback],
        lora_wrapper_obj: Optional[Union[PeftLoraWrapper, LoraWrapper]] = None,
        load_lora_weights: bool = False,
    ) -> Trainer:
        """
        handles the finetuning of a pre-trained model
        """

        if dist.is_initialized():
            logger.info(f"local_rank = {dist.get_rank()}; world_size = {dist.get_world_size()}")
        else:
            logger.info("dist is not initialized")

        logger.info(self.trainer_args)
        trainer = self.trainer_cls(
            model=model,
            train_dataset=self.dataset_args.train_dataset,  # type: ignore
            eval_dataset=self.dataset_args.validation_dataset,  # type: ignore
            compute_metrics=self.metric_func,
            args=self.trainer_args,
            tokenizer=self.tokenizer,
            data_collator=self.dataset_args.data_collator,
            callbacks=trainer_callbacks,
            preprocess_logits_for_metrics=self.preprocess_logits_for_metrics_callback,
        )

        # adding callback to save LoRA models
        if self.optimization_args.apply_lora and lora_wrapper_obj is not None:
            pytorch_save_callback = LoraPyTorchSaveCallback(
                trainer=trainer,
                lora_wrapper_obj=lora_wrapper_obj,
                pytorch_save_folder=self.io_args.pytorch_model_folder,
                optimization_args=self.optimization_args,
                lora_algo=self.optimization_args.lora_algo,
            )
            trainer.add_callback(pytorch_save_callback)
            logger.info("Added LoraPyTorchSaveCallback to Trainer")

        if self.optimization_args.save_on_singularity_preemption:
            trainer.add_callback(ShouldSaveCheckpointOnSingularityPreemption(
                trainer=trainer,
                metadata=self.finetune_args.modelmeta_args.model_metadata,
                model_selector_output=self.finetune_args.io_args.model_selector_output,
                optimization_args = self.optimization_args,
                io_args=self.io_args,
            ))
            logger.info("Added ShouldSaveCheckpointOnSingularityPreemption to Trainer")

        # Add the additional trainbacks supplied by the user
        for user_callback in self.custom_trainer_callbacks:
            trainer.add_callback(user_callback)
            user_callback_name = user_callback if isinstance(user_callback, type) else user_callback.__class__
            logger.info(f"Added user callback {user_callback_name} to Trainer")

        logger.info("Training started!")
        start_time = time.time()
        # Continual Finetuning case
        if load_lora_weights and self.optimization_args.model_name:
            # load the lora weights for the case where model is saved using merge_lora_weights=True
            lora_weights_folder = os.path.join(
                self.io_args.model_selector_output,
                self.optimization_args.model_name,
                AzuremlConstants.LORA_BASE_FOLDER
            )
            logger.info(f"Loading the lora weights from {lora_weights_folder}")
            trainer.load_model_finetuned_weights(resume_from_checkpoint=lora_weights_folder)
        trainer.train(resume_from_checkpoint=self.trainer_args.resume_from_checkpoint)
        end_time = time.time()
        logger.info("Training completed in {} sec".format(end_time - start_time))

        return trainer

    @property
    def should_save(self):
        return self.hf_trainer.args.should_save

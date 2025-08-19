# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

import json
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoConfig, AutoModel
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.trainer_utils import EvalPrediction
from typing import Any, Dict, Optional, Tuple
from pathlib import Path

from azureml.acft.accelerator.constants import HfTrainerMethodsConstants
from azureml.acft.accelerator.constants import HfTrainerType
from azureml.acft.accelerator.finetune import AzuremlFinetuneArgs, AzuremlDatasetArgs
from azureml.acft.accelerator.finetune import AzuremlTrainer
from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults, ModelSelectorConstants
from azureml.acft.common_components.image.runtime_common.common import distributed_utils
from azureml.acft.common_components.utils.mlflow_utils import update_acft_metadata
from azureml.acft.common_components.utils.license_utils import save_license_file
import azureml.acft.multimodal.components.collators.collators as collators
from azureml.acft.multimodal.components.constants.constants \
    import FinetuneParamLiterals, SaveFileConstants, DatasetSplit, Tasks, ModelTypes, \
    DataMode, MMEFTHyperParameterDefaults, PreprocessJsonConstants, ProblemType
from azureml.acft.multimodal.components.data.dataset import AzureMLMultiModalDataset
from azureml.acft.multimodal.components.data.utils import get_dataset_args_from_column_types
import azureml.acft.multimodal.components.image_transformations.transformations as transformations
from azureml.acft.multimodal.components.mlflow.mlflow_save_utils import save_multimodal_mlflow_pyfunc_model
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_config import AzuremlMMEarlyFusionConfig
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_model import (
    AzuremlMMEarlyFusionModelForClassification, create_optimizer_custom_func
)
from azureml.metrics import compute_metrics, constants

logger = get_logger_app(__name__)


class FinetuneForMmeft:

    def __init__(self, finetune_params: Dict[str, Any]) -> None:

        AutoConfig.register(ModelTypes.MMEFT, AzuremlMMEarlyFusionConfig)
        AutoModel.register(AzuremlMMEarlyFusionConfig, AzuremlMMEarlyFusionModelForClassification)

        logger.info(f"Task name: {Tasks.MUTIMODAL_CLASSIFICATION}")

        # finetune params is finetune component args + args saved as part of preprocess
        self.finetune_params = finetune_params
        self.finetune_params.update({
            "dataloader_drop_last": False,
            "remove_unused_columns": False,
        })
        self.model_type = ModelTypes.MMEFT
        self.is_multilabel = \
            (finetune_params[PreprocessJsonConstants.PROBLEM_TYPE] == ProblemType.MULTI_LABEL_CLASSIFICATION)

        # Load class names
        class_names_load_path = Path(self.finetune_params["preprocess_output"], SaveFileConstants.CLASSES_SAVE_PATH)
        with open(class_names_load_path, 'r') as rptr:
            class_names = json.load(rptr)[SaveFileConstants.CLASSES_SAVE_KEY]
            self.finetune_params["class_names"] = class_names
            self.finetune_params["num_labels"] = len(self.finetune_params["class_names"])
            self.finetune_params["id2label"] = {idx: lbl for idx, lbl in enumerate(class_names)}
            self.finetune_params["label2id"] = {lbl: idx for idx, lbl in enumerate(class_names)}

    def _get_finetune_args(self) -> AzuremlFinetuneArgs:

        azml_trainer_finetune_args = AzuremlFinetuneArgs(
            self.finetune_params,
            trainer_type=HfTrainerType.DEFAULT
        )

        return azml_trainer_finetune_args

    def _get_dataset_args(
            self, tokenizer: Optional[PreTrainedTokenizerBase] = None
    ) -> Tuple[AzuremlDatasetArgs, Dict[str, Any]]:

        train_file_path = os.fspath(Path(self.finetune_params["preprocess_output"], "train.jsonl"))
        valid_file_path = os.fspath(Path(self.finetune_params["preprocess_output"], "validation.jsonl"))

        column_types_path = os.fspath(Path(self.finetune_params["preprocess_output"],
                                           SaveFileConstants.COLUMN_TYPES_SAVE_PATH))
        dataset_args = get_dataset_args_from_column_types(column_types_path)

        train_ds = AzureMLMultiModalDataset(
            jsonl_path=train_file_path, data_split=DatasetSplit.TRAIN,
            dataset_args=dataset_args,
            collation_fn=collators.get_collation_function(model_type=self.model_type),
            image_transforms_fn=transformations.get_transform_function(model_type=self.model_type),
            label2id=self.finetune_params["label2id"],
            tabular_featurizer=None,
            text_tokenizer=tokenizer,
            processor=None,
            is_multilabel=self.is_multilabel,
        )

        train_tabular_featurizer = train_ds.get_tabular_featurizer()
        if train_tabular_featurizer is not None:
            tabular_featurizer_path = os.path.join(self.finetune_params["output_dir"],
                                                   SaveFileConstants.TABULAR_FEATURIZER)
            with open(tabular_featurizer_path, "wb") as featurizer_fp:
                pickle.dump(train_tabular_featurizer, featurizer_fp)

        validation_ds = AzureMLMultiModalDataset(
            jsonl_path=valid_file_path, data_split=DatasetSplit.VALIDATION,
            dataset_args=dataset_args,
            collation_fn=collators.get_collation_function(model_type=self.model_type),
            image_transforms_fn=transformations.get_transform_function(model_type=self.model_type),
            label2id=self.finetune_params["label2id"],
            tabular_featurizer=train_tabular_featurizer,
            text_tokenizer=tokenizer,
            processor=None,
            is_multilabel=self.is_multilabel,
        )

        azml_trainer_dataset_args = AzuremlDatasetArgs(
            train_dataset=train_ds.dataset,
            validation_dataset=validation_ds.dataset,
            data_collator=train_ds.get_collation_function()
        )

        dataset_properties = {
            "num_numerical_features": train_ds.get_num_numericals(),
            "categorical_cardinalities": train_ds.get_categorical_cardinalities(),
            "num_text_columns": train_ds.get_num_text_columns(),
            "modes": train_ds.get_modes()
        }
        return azml_trainer_dataset_args, dataset_properties

    def _load_model(self, num_numerical_features, categorical_cardinalities, num_text_columns, modes) -> nn.Module:

        model_params = {
            "num_numerical_features": num_numerical_features,
            "categorical_cardinalities": categorical_cardinalities,
            "num_classes": self.finetune_params["num_labels"],
            "id2label": self.finetune_params["id2label"],
            "label2id": self.finetune_params["label2id"],
            "batch_size": self.finetune_params["per_device_train_batch_size"],
            "num_text_cols": num_text_columns,
            "modes": modes
        }

        config = AzuremlMMEarlyFusionConfig.from_pretrained(self.finetune_params["model_name_or_path"], **model_params)
        model = AzuremlMMEarlyFusionModelForClassification.from_pretrained(
            self.finetune_params["model_name_or_path"], config=config, ignore_mismatched_sizes=True)

        if self.is_multilabel:
            model.loss = nn.BCEWithLogitsLoss()
        else:
            model.loss = nn.CrossEntropyLoss()

        return model

    def _get_tokenizer(self) -> PreTrainedTokenizerBase:
        return AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=False)

    def finetune(self) -> None:
        tokenizer = self._get_tokenizer()
        dataset_args, dataset_properties = self._get_dataset_args(tokenizer=tokenizer)

        model = self._load_model(**dataset_properties)

        custom_trainer_functions = {
            HfTrainerMethodsConstants.AZUREML_OPTIMIZER: create_optimizer_custom_func
        }

        tabular_featurizer_path = None
        if DataMode.TABULAR in dataset_properties["modes"]:
            tabular_featurizer_path = os.fspath(Path(self.finetune_params[FinetuneParamLiterals.OUTPUT_DIR],
                                                     SaveFileConstants.TABULAR_FEATURIZER))

        trainer = AzuremlTrainer(
            finetune_args=self._get_finetune_args(),
            dataset_args=dataset_args,
            model=model,
            tokenizer=tokenizer,
            metric_func=self.compute_metrics_func,
            custom_trainer_functions=custom_trainer_functions
        )

        # Torch barrier is used to complete the training on a distributed setup
        # Use callbacks for adding steps to be done at the end of training
        # NOTE Avoid adding any logic after trainer.train()
        # Test the distributed scenario in case you add any logic beyond trainer.train()
        trainer.train()

        master_process = distributed_utils.master_process()
        if master_process:
            # Best pytorch model is not separately saved when trainer callbacks are called.
            # Hence, have to run after trainer.train() is complete.
            preprocess_output_dir = self.finetune_params[FinetuneParamLiterals.PREPROCESS_OUTPUT]
            best_pytorch_model_dir = self.finetune_params[FinetuneParamLiterals.PYTORCH_MODEL_DIR]
            mlflow_output_dir = self.finetune_params[FinetuneParamLiterals.MLFLOW_MODEL_DIR]

            # Fetch meta data of model
            finetuning_task = Tasks.MULTIMODAL_MULTILABEL_CLASSIFICATION if self.is_multilabel else\
                Tasks.MUTIMODAL_CLASSIFICATION
            metadata = self.finetune_params.get(ModelSelectorConstants.MODEL_METADATA, {})
            metadata = update_acft_metadata(metadata=metadata,
                                            finetuning_task=finetuning_task)

            # Save model in MLFlow format
            save_multimodal_mlflow_pyfunc_model(preprocess_output_dir, best_pytorch_model_dir, mlflow_output_dir,
                                                tabular_featurizer_path, metadata)

            # Save license file in MLflow export
            save_license_file(
                model_name_or_path=ModelTypes.MMEFT,
                license_file_name=ModelSelectorDefaults.LICENSE_FILE_NAME,
                destination_paths=[best_pytorch_model_dir, mlflow_output_dir]
            )

    def compute_metrics_func(self, eval_pred: EvalPrediction):
        """
        compute and return metrics for multi class classification
        """
        predictions, labels = eval_pred
        if self.is_multilabel:
            sigmoid = torch.nn.Sigmoid()
            probs = sigmoid(torch.Tensor(predictions)).numpy()
            y_pred_fusion = np.zeros(probs.shape)
            y_pred_fusion[np.where(probs >= MMEFTHyperParameterDefaults.CLASS_SCORE_THRESHOLD)] = 1
            y_true = labels
        else:
            y_pred_fusion = np.argmax(predictions, axis=1)
            y_true = np.squeeze(labels, axis=1)

        result = compute_metrics(task_type=constants.Tasks.CLASSIFICATION,
                                 y_test=y_true,
                                 y_pred=y_pred_fusion,
                                 multilabel=self.is_multilabel)
        return result["metrics"]

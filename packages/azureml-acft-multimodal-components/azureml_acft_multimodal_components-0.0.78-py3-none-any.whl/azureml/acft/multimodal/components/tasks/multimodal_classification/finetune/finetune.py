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
import os
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import torch.nn as nn

from azureml.acft.accelerator.finetune import AzuremlFinetuneArgs, AzuremlDatasetArgs
from azureml.acft.accelerator.finetune import AzuremlTrainer
from azureml.acft.accelerator.constants import HfTrainerType

from azureml.acft.multimodal.components.artifacts.tokenizer import AzuremlCLIPTokenizer
from azureml.acft.multimodal.components.artifacts.preprocessor import AzuremlCLIPProcessor
from azureml.acft.multimodal.components.artifacts.model import AzuremlAutoMLMultiModel, AzuremlAutoMLMultiModelConfig
from azureml.acft.multimodal.components.data.dataset import AzureMLMultiModalDataset
from azureml.acft.multimodal.components.data.utils import get_dataset_args_from_column_types
from azureml.acft.multimodal.components.constants.constants import SaveFileConstants, DatasetSplit, ModelTypes, \
    Tasks, DataMode
from azureml.acft.multimodal.components.utils.trainer_callbacks import SaveMLflowModelCallback

from transformers import PreTrainedTokenizerBase

from azureml.acft.common_components import get_logger_app, ModelSelectorConstants
import azureml.acft.multimodal.components.collators.collators as collators
import azureml.acft.multimodal.components.image_transformations.transformations as transformations

logger = get_logger_app(__name__)


class SingleLabelFinetune:

    def __init__(self, finetune_params: Dict[str, Any]) -> None:
        logger.info(f"Task name: {Tasks.MUTIMODAL_CLASSIFICATION}")

        self.finetune_params = finetune_params
        self.finetune_params["remove_unused_columns"] = False
        self.tokenizer = self._get_tokenizer()
        self.model_type = ModelTypes.CLIP
        self.preprocessor = self._get_processor()
        # if :param `resume_from_checkpoint` is set to True
        #   - only load the weights using config while creating model object
        #   - update the `resume_from_checkpoint` to the model_name_or_path to load the model, and optimizer and
        #     scheduler states if exist
        if self.finetune_params.pop("resume_from_checkpoint", False) \
                and isinstance(self.finetune_params["model_name_or_path"], Path) \
                and self.finetune_params["model_name_or_path"].is_dir():
            self.finetune_params["resume_from_checkpoint"] = self.finetune_params["model_name_or_path"]

        # Load class names
        class_names_load_path = Path(self.finetune_params["preprocess_output"], SaveFileConstants.CLASSES_SAVE_PATH)
        with open(class_names_load_path, 'r') as rptr:
            class_names = json.load(rptr)[SaveFileConstants.CLASSES_SAVE_KEY]
            self.finetune_params["class_names"] = class_names
            self.finetune_params["num_labels"] = len(self.finetune_params["class_names"])
            self.finetune_params["id2label"] = {idx: lbl for idx, lbl in enumerate(class_names)}
            self.finetune_params["label2id"] = {lbl: idx for idx, lbl in enumerate(class_names)}

        logger.info(self.finetune_params)

    def _get_finetune_args(self, model_type: Optional[str] = None) -> AzuremlFinetuneArgs:
        self.finetune_params["model_type"] = model_type
        azml_trainer_finetune_args = AzuremlFinetuneArgs(
            self.finetune_params,
            trainer_type=HfTrainerType.DEFAULT
        )

        return azml_trainer_finetune_args

    def _get_save_featurizer(self, train_ds):
        train_tabular_featurizer = train_ds.get_tabular_featurizer()
        if train_tabular_featurizer is not None:
            if not os.path.exists(self.finetune_params["output_dir"]):
                os.mkdir(self.finetune_params["output_dir"])
            tabular_featurizer_path = os.path.join(self.finetune_params["output_dir"],
                                                   SaveFileConstants.TABULAR_FEATURIZER)
            with open(tabular_featurizer_path, "wb") as featurizer_fp:
                pickle.dump(train_tabular_featurizer, featurizer_fp)
        return train_tabular_featurizer

    def _get_dataset_args(self) -> Tuple[AzuremlDatasetArgs, Dict[str, Any]]:
        train_file_path = os.fspath(Path(self.finetune_params["preprocess_output"], "train.jsonl"))
        valid_file_path = os.fspath(Path(self.finetune_params["preprocess_output"], "validation.jsonl"))

        column_types_path = os.fspath(Path(self.finetune_params["preprocess_output"],
                                           SaveFileConstants.COLUMN_TYPES_SAVE_PATH))
        dataset_args = get_dataset_args_from_column_types(column_types_path=column_types_path)

        train_ds = AzureMLMultiModalDataset(
            jsonl_path=train_file_path, data_split=DatasetSplit.TRAIN,
            dataset_args=dataset_args,
            collation_fn=collators.get_collation_function(model_type=self.model_type),
            image_transforms_fn=transformations.get_transform_function(model_type=self.model_type),
            label2id=self.finetune_params["label2id"],
            tabular_featurizer=None,
            text_tokenizer=self.tokenizer,
            processor=self.preprocessor,
        )
        train_tabular_featurizer = self._get_save_featurizer(train_ds)

        validation_ds = AzureMLMultiModalDataset(
            jsonl_path=valid_file_path, data_split=DatasetSplit.VALIDATION,
            collation_fn=collators.get_collation_function(model_type=self.model_type),
            image_transforms_fn=transformations.get_transform_function(model_type=self.model_type),
            dataset_args=dataset_args,
            label2id=self.finetune_params["label2id"],
            tabular_featurizer=train_tabular_featurizer,
            text_tokenizer=self.tokenizer,
            processor=self.preprocessor,
        )
        azml_trainer_dataset_args = AzuremlDatasetArgs(
            train_dataset=train_ds.dataset,
            validation_dataset=validation_ds.dataset,
            data_collator=train_ds.get_collation_function()
        )

        dataset_properties = {
            "modes": train_ds.get_modes()
        }

        return azml_trainer_dataset_args, dataset_properties

    def _load_model(self) -> nn.Module:
        kwargs = {
            "num_labels": self.finetune_params["num_labels"],
            "id2label": self.finetune_params["id2label"],
            "label2id": self.finetune_params["label2id"],
            "model_name_or_path": self.finetune_params["model_name_or_path"]
        }
        config = AzuremlAutoMLMultiModelConfig.from_pretrained(self.finetune_params["model_name_or_path"], **kwargs)
        return AzuremlAutoMLMultiModel.from_pretrained(self.finetune_params["model_name_or_path"], config=config)

    def _get_processor(self):
        return AzuremlCLIPProcessor.from_pretrained(
            self.finetune_params["model_name_or_path"])

    def _get_tokenizer(self) -> PreTrainedTokenizerBase:
        tokenizer_params = {
            "revision": None
        }
        # ToDO: Check if this needs to be loaded from self.finetune_params["preprocess_output"]
        return AzuremlCLIPTokenizer.from_pretrained(
            self.finetune_params["model_name_or_path"], **tokenizer_params)

    def finetune(self) -> None:
        column_types_path = os.fspath(Path(self.finetune_params["preprocess_output"],
                                           SaveFileConstants.COLUMN_TYPES_SAVE_PATH))
        preprocess_args_path = os.fspath(Path(self.finetune_params["preprocess_output"],
                                              SaveFileConstants.PREPROCESS_ARGS_SAVE_PATH))
        dataset_args, dataset_properties = self._get_dataset_args()
        model = self._load_model()

        extra_files = [preprocess_args_path, column_types_path]
        if DataMode.TABULAR in dataset_properties["modes"]:
            tabular_featurizer_path = os.fspath(Path(self.finetune_params["output_dir"],
                                                     SaveFileConstants.TABULAR_FEATURIZER))
            extra_files.append(tabular_featurizer_path)

        save_mlflow_callback = SaveMLflowModelCallback(
            mlflow_model_save_path=self.finetune_params["mlflow_model_folder"],
            mlflow_task_type="text-classification",
            model_name_or_path=self.finetune_params["model_name_or_path"],
            preprocessor=self.preprocessor,
            model_type=self.model_type,
            extra_files=extra_files,
            base_model_asset_id=self.finetune_params.get(ModelSelectorConstants.BASE_MODEL_ASSET_ID, None),
            base_model_task=self.finetune_params.get(ModelSelectorConstants.BASE_MODEL_TASK, None),
        )

        trainer = AzuremlTrainer(
            finetune_args=self._get_finetune_args(),
            dataset_args=dataset_args,
            model=model,
            tokenizer=self.tokenizer,
            metric_func=None,
            custom_trainer_callbacks=[save_mlflow_callback],
        )

        # Torch barrier is used to complete the training on a distributed setup
        # Use callbacks for adding steps to be done at the end of training
        # NOTE Avoid adding any logic after trainer.train()
        # Test the distributed scenario in case you add any logic beyond trainer.train()
        trainer.train()

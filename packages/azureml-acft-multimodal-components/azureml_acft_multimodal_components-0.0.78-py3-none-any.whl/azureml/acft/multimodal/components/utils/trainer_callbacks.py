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
"""
mlflow utilities
"""
from mlflow.models import Model
import os
from pathlib import Path
from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from typing import Union
from mlflow.models import Model

from ..constants.constants import MLFlowHFFlavourConstants, ModelTypes
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.mlflow_utils import update_acft_metadata
import azureml.evaluate.mlflow as mlflow

logger = get_logger_app(__name__)


class SaveMLflowModelCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(
            self,
            mlflow_model_save_path: Union[str, Path],
            mlflow_task_type: str,
            model_name_or_path: str,
            model_type: str,
            metadata: dict,
            **kwargs
    ) -> None:
        """
        init azureml_run which is azureml Run object
        """
        self.mlflow_model_save_path = mlflow_model_save_path
        self.mlflow_task_type = mlflow_task_type
        self.model_name_or_path = model_name_or_path
        self.model_type = model_type
        self.processor = kwargs["preprocessor"]
        self.extra_files = kwargs["extra_files"]
        self.metadata = metadata
        self.conda_env = {
            'channels': ['conda-forge'],
            'dependencies': [
                'python=3.8.8',
                'pip',
                {'pip': [
                    'mltable==1.5.0',
                    'mlflow==2.6.0',
                    'datasets==2.12.0',
                    'torch~=1.13.1',
                    'transformers==4.29.1',
                    'azureml-evaluate-mlflow==0.0.28',
                    'azureml-acft-accelerator==0.0.28',
                    'azureml-acft-common-components==0.0.28',
                    #'azureml-acft-contrib-hf-nlp==0.0.28',
                    'https://automlcesdkdataresources.blob.core.windows.net/finetuning-multimodal-models/wheels/mmeft/azureml_acft_contrib_hf_nlp-0.1.0.0-py3-none-any.whl',
                    'https://automlcesdkdataresources.blob.core.windows.net/finetuning-multimodal-models/wheels/mmeft/azureml_acft_multimodal_components-0.1.0.0-py3-none-any.whl',
                ]}
            ],
            'name': 'mlflow-env'
        }

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """
        Event called at the end of training.
        Save MLflow model at the end of training

        Model and Tokenizer information is part of kwargs
        """

        model, tokenizer = kwargs["model"], self.processor

        # saving the mlflow on world process 0
        if state.is_world_process_zero:
            misc_conf = {
                MLFlowHFFlavourConstants.TASK_TYPE: self.mlflow_task_type,
                MLFlowHFFlavourConstants.HUGGINGFACE_ID: self.model_name_or_path,
            }
            if self.model_type == ModelTypes.CLIP:
                misc_conf.update({
                    "custom_config_module": "model",
                    "custom_tokenizer_module": "preprocessor",
                    "custom_model_module": "model",
                    "hf_predict_module": "multimodal_clip_predict"
                })
                base_pkg__path = Path(__file__).parent.parent
                files_list = [os.path.join(base_pkg__path, file) for file in ["artifacts/model.py",
                                                                              "artifacts/preprocessor.py",
                                                                              "data/dataset.py",
                                                                              "artifacts/multimodal_clip_predict.py",
                                                                              "artifacts/multimodal_mmeft_predict.py",
                                                                              "image_transformations/transformations.py",
                                                                              "collators/collators.py"]]

                metadata = update_acft_metadata(metadata=self.metadata,
                                                finetuning_task=self.mlflow_task_type)
                # This is to unify hfv2/OSS metadata dump
                mlflow_model = Model(metadata=metadata)

                mlflow.hftransformers.save_model(
                    model, self.mlflow_model_save_path, tokenizer, model.config,
                    misc_conf,
                    code_paths=files_list,
                    conda_env=self.conda_env,
                    mlflow_model=mlflow_model,
                    extra_files=self.extra_files)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base runner
"""

from abc import ABC, abstractmethod

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


class BaseRunner(ABC):

    def check_model_task_compatibility(self, model_name_or_path: str, task_name: str) -> None:
        """
        Check if the given model supports the given task in the case of Hugging Face Models
        """
        pass

    @abstractmethod
    def run_preprocess_for_finetune(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def run_finetune(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def run_finetune_for_mmeft(self, *args, **kwargs) -> None:
        pass

    def run_modelselector(self, **kwargs) -> None:
        """
        Downloads model from azureml-preview registry if present
        Prepares model for continual finetuning
        Save model selector args
        """
        pass

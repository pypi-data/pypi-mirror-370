# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
model selector utils
"""

import os
from pathlib import Path
from typing import Dict, Any, Union
import shutil
import yaml
import json

from azureml.acft.common_components import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError, MissingData
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.multimodal.components.constants.constants import SaveFileConstants, MLFlowHFFlavourConstants, \
    MLFlowPyfuncLiterals

logger = get_logger_app(__name__)


MODEL_REGISTRY_NAME = "azureml"


def get_model_name_from_pytorch_model(model_path: str) -> str:
    """
    Fetch model_name information from pytorch model metadata file
    """
    finetune_args_file = os.path.join(model_path, SaveFileConstants.FINETUNE_ARGS_SAVE_PATH)

    # load the metadata file
    try:
        with open(finetune_args_file, "r") as rptr:
            finetune_args = json.load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {finetune_args_file}\n"
                f"{e}"
                )
            )
        )

    # check for `model_name` in metadata file
    if finetune_args and "model_name" in finetune_args:
        return finetune_args["model_name"]
    else:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"model_name is missing in "
                f"{SaveFileConstants.FINETUNE_ARGS_SAVE_PATH} file"
                )
            )
        )


def get_model_name_from_hf_mlflow_model(model_path: str) -> str:
    """
    Fetch model_name information from mlflow metadata file
    """
    mlflow_config_file = Path(model_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)

    # load mlflow config file
    try:
        with open(mlflow_config_file, "r") as rptr:
            mlflow_data = yaml.safe_load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {mlflow_config_file}\n"
                f"{e}"
                )
            )
        )

    # fetch the model name
    try:
        if mlflow_data and MLFlowHFFlavourConstants.HUGGINGFACE_ID in mlflow_data["flavors"]["hftransformers"]:
            return mlflow_data["flavors"]["hftransformers"][MLFlowHFFlavourConstants.HUGGINGFACE_ID]
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                "{Invalid mlflow config file}\n"
                f"{e}"
                )
            )
        )


def is_mlflow_pyfun_flavour(model_path: str) -> bool:
    """
    Check if mlflow model is in pyfunc format

    :param model_path: Path to mlflow folder
    :type model_path: str
    :return: Return True if mlflow model is in pyfunc format
    :rtype: bool
    """
    mlflow_config_file = os.path.join(model_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)

    try:
        # load mlflow config file
        with open(mlflow_config_file, "r") as rptr:
            mlflow_data = yaml.safe_load(rptr)
        return mlflow_data["flavors"]["python_function"]["loader_module"] == MLFlowPyfuncLiterals.PYFUNC_LOADER_MODULE

    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {mlflow_config_file}\n"
                f"{e}"
                )
            )
        )


def get_model_name_from_pyfunc_mlflow(model_path: str) -> str:
    """
    Fetch model_name information from mlflow directory

    :param model_path: Path to mlflow folder.
    :type model_path: str
    :return: Name of the model that's present in mlflow folder
    :rtype: str
    """
    mlflow_config_file = os.path.join(model_path, MLFlowPyfuncLiterals.ARTIFACTS_DIR,
                                      MLFlowPyfuncLiterals.PYTORCH_MODEL_DIR,
                                      MLFlowPyfuncLiterals.CONFIG_JSON)

    # fetch the model name
    try:
        if os.path.exists(mlflow_config_file):
            with open(mlflow_config_file, "r") as rptr:
                model_config_params = json.load(rptr)

            logger.info(f"{model_config_params['model_type']} model found in mlflow format.")
            return model_config_params["model_type"]
        else:
            raise LLMException._with_error(
                AzureMLError.create(LLMInternalError, error=(
                    f"File not found at path {mlflow_config_file} in mlflow folder\n")
                    )
                )
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                "{Invalid mlflow config file}\n"
                f"{e}"
                )
            )
        )


def convert_hf_mlflow_to_pytorch_model(mlflow_model_path: Union[str, Path], download_dir: str):
    """
    converts mlflow model to pytorch model
    """

    os.makedirs(download_dir, exist_ok=True)

    try:
        # copy the model and config files
        shutil.copytree(
            Path(mlflow_model_path, 'data/model'),
            download_dir,
            dirs_exist_ok=True
        )
        # copy tokenizer files
        shutil.copytree(
            Path(mlflow_model_path, 'data/tokenizer'),
            download_dir,
            dirs_exist_ok=True
        )
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise LLMException._with_error(
            AzureMLError.create(
                LLMInternalError,
                error=(
                    "Failed to convert mlflow model to pytorch model.\n"
                    f"{e}"
                )
            )
        )


def convert_pyfunc_mlflow_to_pytorch_model(mlflow_model_path: str, download_dir: str):
    """
    Converts mlflow model to pytorch model. This is only for raw (not-finetuned) model.

    :param mlflow_model_path: Path to mlflow folder.
    :type mlflow_model_path: str
    :param download_dir: Path to folder where we need to place pytorch format of model.
    :type download_dir: str
    """
    logger.info("converting pyfunc flavoured mlflow model to pytorch")

    os.makedirs(download_dir, exist_ok=True)

    try:
        shutil.copytree(
            os.path.join(mlflow_model_path, MLFlowPyfuncLiterals.ARTIFACTS_DIR, MLFlowPyfuncLiterals.PYTORCH_MODEL_DIR),
            download_dir,
            dirs_exist_ok=True
        )
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise LLMException._with_error(
            AzureMLError.create(
                LLMInternalError,
                error=(
                    "Failed to convert mlflow model to pytorch model.\n"
                    f"{e}"
                )
            )
        )


def model_selector(model_selector_args: Dict[str, Any]):
    """
    Downloads model from azureml-preview registry if present
    Prepares model for continual finetuning
    Save model selector args
    """
    logger.info(f"Model Selector args - {model_selector_args}")
    # pytorch model port
    pytorch_model_path = model_selector_args.get("pytorch_model_path", None)
    # mlflow model port
    mlflow_model_path = model_selector_args.get("mlflow_model_path", None)

    # if both pytorch and mlflow model ports are specified, pytorch port takes precedence
    if pytorch_model_path is not None:
        logger.info("Working with pytorch model")
        # copy model to download_dir
        model_name = get_model_name_from_pytorch_model(pytorch_model_path)
        model_selector_args["model_name"] = model_name
        download_dir = os.path.join(model_selector_args["output_dir"], model_name)
        download_dir.mkdir(exist_ok=True)
        try:
            shutil.copytree(pytorch_model_path, download_dir, dirs_exist_ok=True)
        except Exception as e:
            shutil.rmtree(download_dir, ignore_errors=True)
            raise LLMException._with_error(
                AzureMLError.create(
                    LLMInternalError,
                    error=(
                        "shutil copy failed.\n"
                        f"{e}"
                    )
                )
            )
    elif mlflow_model_path is not None:
        logger.info("Working with Mlflow model")
        is_pyfunc_flavour = is_mlflow_pyfun_flavour(mlflow_model_path)
        if is_pyfunc_flavour:
            model_name = get_model_name_from_pyfunc_mlflow(mlflow_model_path)
        else:
            model_name = get_model_name_from_hf_mlflow_model(mlflow_model_path)

        model_selector_args["model_name"] = model_name
        download_dir = os.path.join(model_selector_args["output_dir"], model_name)

        # convert mlflow model to pytorch model and save it to model_save_path
        if is_pyfunc_flavour:
            convert_pyfunc_mlflow_to_pytorch_model(mlflow_model_path, download_dir)
        else:
            convert_hf_mlflow_to_pytorch_model(mlflow_model_path, download_dir)
    else:
        logger.error("missing mlflow and pytorch model path")
        raise LLMException._with_error(AzureMLError.create(MissingData, data_argument_name="model_path"))

    # Saving model selector args
    model_selector_args_save_path = os.path.join(model_selector_args["output_dir"],
                                                 SaveFileConstants.MODEL_SELECTOR_ARGS_SAVE_PATH)
    logger.info(f"Saving the model selector args to {model_selector_args_save_path}")
    with open(model_selector_args_save_path, "w") as wptr:
        json.dump(model_selector_args, wptr, indent=2)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Save pytorch models as Mlflow."""
import mlflow
from os.path import dirname, join

from azureml.acft.multimodal.components.constants.constants import (
    MLFlowPyfuncLiterals, FinetuneParamLiterals, SaveFileConstants
)
from azureml.acft.multimodal.components.mlflow.mlflow_model_wrapper import MultimodalMLFlowModelWrapper
from azureml.acft.common_components import get_logger_app

logger = get_logger_app(__name__)


def save_multimodal_mlflow_pyfunc_model(
    preprocess_output_dir: str,
    pytorch_model_dir: str,
    mlflow_output_dir: str,
    tabular_featurizer_pkl: str,
    metadata: dict
) -> None:
    """
    Save the multimodal model in mlflow format using pyfunc flavour.

    :param preprocess_output_dir: Output directory
    :type preprocess_output_dir: str
    :param pytorch_model_dir: Output directory where finetuned pytorch model is saved.
    :type pytorch_model_dir: str
    :param mlflow_output_dir: Output directory where model should be saved in mlflow format.
    :type mlflow_output_dir: str
    :param tabular_featurizer_pkl: Name of the model.
    :type tabular_featurizer_pkl: str
    :param metadata: Metadata of the model.
    :type metadata: dict
    """

    logger.info("Saving the model in MLFlow format.")

    files_to_include = [join("mlflow", "mlflow_model_wrapper.py")
                        # join("artifacts", "model.py"),
                        # join("artifacts", "preprocessor.py"),
                        # join("data", "dataset.py"),
                        # join("artifacts", "multimodal_mmeft_predict.py"),
                        # join("image_transformations", "transformations.py"),
                        # join("collators", "collators.py")
                        ]
    directory = dirname(dirname(__file__))
    code_path = [join(directory, x) for x in files_to_include]

    artifacts_dict = {
        MLFlowPyfuncLiterals.CHECKPOINT_FOLDER: pytorch_model_dir,
        MLFlowPyfuncLiterals.TABULAR_FEATURIZER_PKL: tabular_featurizer_pkl,
        FinetuneParamLiterals.PREPROCESS_OUTPUT: preprocess_output_dir
    }

    logger.info(f"Saving mlflow pyfunc model to {mlflow_output_dir}.")

    try:
        mlflow.pyfunc.save_model(
            path=mlflow_output_dir,
            python_model=MultimodalMLFlowModelWrapper(),
            artifacts=artifacts_dict,
            conda_env=join(dirname(__file__), SaveFileConstants.CONDA_YAML),
            code_path=code_path,
            metadata=metadata
        )
        logger.info("Saved mlflow model successfully.")
    except Exception as e:
        logger.error(f"Failed to save the mlflow model {str(e)}")
        raise Exception(f"failed to save the mlflow model {str(e)}")

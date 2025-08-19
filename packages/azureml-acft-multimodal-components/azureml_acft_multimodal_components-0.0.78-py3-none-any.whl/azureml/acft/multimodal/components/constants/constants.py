# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants"""

from dataclasses import dataclass


@dataclass
class DatasetSplit:
    TEST = "test"
    TRAIN = "train"
    VALIDATION = "validation"


@dataclass
class SaveFileConstants:
    """
    A class to represent constants for metadata related to saving the model.
    """

    PREPROCESS_ARGS_SAVE_PATH = "preprocess_args.json"
    FINETUNE_ARGS_SAVE_PATH = "finetune_args.json"
    CLASSES_SAVE_PATH = "class_names.json"
    ID2LABEL_SAVE_PATH = "id2label.json"
    LABEL2ID_SAVE_PATH = "label2id.json"
    CLASSES_SAVE_KEY = "class_names"
    MODEL_SELECTOR_ARGS_SAVE_PATH = "model_selector_args.json"
    COLUMN_TYPES_SAVE_PATH = "column_types.json"
    TABULAR_FEATURIZER = "tabular_featurizer.pkl"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_PYTORCH_OUTPUT = "pytorch_output"
    DEFAULT_MLFLOW_OUTPUT = "mlflow_output"
    CONDA_YAML = "conda.yaml"

@dataclass
class MLFlowHFFlavourConstants:
    """
    A class to represent constants for parameters of HF Flavour mlflow.
    """
    TRAIN_LABEL_LIST = "train_label_list"
    TASK_TYPE = "task_type"
    # NOTE ONLY used for Summarization and Translation tasks
    PREFIX_AND_TASK_FILE_SAVE_NAME_WITH_EXT = "azureml_tokenizer_prefix_mlflow_task.json"
    PREFIX_SAVE_KEY = "tokenizer_prefix"

    TASK_SAVE_KEY = "mlflow_task"
    INFERENCE_PARAMS_SAVE_NAME_WITH_EXT = "azureml_mlflow_inference_params.json"
    INFERENCE_PARAMS_SAVE_KEY = "tokenizer_config"
    MISC_CONFIG_FILE = "MLmodel"
    MODEL_ROOT_DIRECTORY = "mlflow_model_folder"
    HUGGINGFACE_ID = "huggingface_id"


class MLFlowTasks:
    """
    A class to represent constants for MLFlow supported tasks.
    """
    MULTIMODAL_CLASSIFICATION = "multimodal-classification"


class AdditionalFeatureType:
    """
    A class to represent feature types that are not recognized by column purpose detection from automl runtime.
    """
    Image = "Image"
    Label = "Label"


@dataclass
class ColumnTypesInfoLiterals:
    """Literals used in column types information."""
    COLUMN_TYPES = "column_types"
    COLUMN_TYPE = "column_type"
    COLUMN_NAME = "column_name"
    COLUMN_PREFIX = "Azureml_"


@dataclass
class ColumnTypesValue:
    """Literals used as values for column types."""
    CATEGORICAL = "Categorical"
    NUMERIC = "Numeric"
    IMAGE = "Image"
    TEXT = "Text"
    LABEL = "Label"


@dataclass
class ModelTypes:
    CLIP = "clip"
    MMEFT = "mmeft"


@dataclass
class Tasks:
    """Supported Tasks"""
    MUTIMODAL_CLASSIFICATION = "MultiModalClassification"
    MULTIMODAL_MULTILABEL_CLASSIFICATION = "MultiModalMultiLabelClassification"


@dataclass
class ProblemType:
    """Supported problem_types"""
    SINGLE_LABEL_CLASSIFICATION = "multimodal-classification-singlelabel"
    MULTI_LABEL_CLASSIFICATION = "multimodal-classification-multilabel"


@dataclass
class DataMode:
    """Data modes"""
    TABULAR = "tabular"
    TEXT = "text"
    IMAGE = "image"


@dataclass
class MLFlowHFFlavourPredictConstants:
    """
    Constants for parameters used in predict for HF Flavour mlflow.
    """
    EXTRA_FILES = "extra_files"
    PATH = "path"


@dataclass
class PreprocessJsonConstants:
    """
    Constants for arguments in preprocess_args.json
    """
    DATASET_COLUMNS = "dataset_columns"
    IGNORE_COLUMNS = "ignore_columns"
    PASS_THROUGH_COLUMNS = "pass_through_columns"
    LABEL_COLUMN = "label_column"
    PROBLEM_TYPE = "problem_type"


@dataclass
class MMEFTHyperParameterDefaults:
    """
    Default hyperparameter values for MMEFT model.
    """
    EMBEDDING_SIZE = 64  # d
    TEXT_EMBEDDING_SIZE = 768
    VISION_EMBEDDING_SIZE = 1000
    NUM_TRANSFORMER_HEADS = 8
    NUM_TRANSFORMER_LAYERS = 6
    TRANSFORMER_DROPOUT = 0.1
    EMBEDDING_DROPOUT = 0.1
    LEARNING_RATE = 0.001
    WARMUP_RATIO = 0.33
    TRAINING_BATCH_SIZE = 8
    VALIDATION_BATCH_SIZE = 64
    GRADIENT_ACCUMULATION_STEPS = 64
    CLASS_SCORE_THRESHOLD = 0.5


@dataclass
class FinetuneParamLiterals:
    """
    Literals related to parameters in finetuning component.
    """
    PREPROCESS_OUTPUT = "preprocess_output"
    PYTORCH_MODEL_DIR = "pytorch_model_folder"
    OUTPUT_DIR = "output_dir"
    MLFLOW_MODEL_DIR = "mlflow_model_folder"
    MODEL_NAME = "model_name"
    MODEL_NAME_OR_PATH = "model_name_or_path"


@dataclass
class MLFlowPyfuncLiterals:
    """
    Literals related to saving and loading Multimodal modal in Mlflow format via pyfunc.
    """
    CHECKPOINT_FOLDER = "checkpoint_folder"
    DATATSET_FEATURES = "dataset_features"
    TABULAR_FEATURIZER_PKL = "tabular_featurizer_pkl"
    SCHEMA_SIGNATURE = "signature"
    WRAPPER = "multimodal_model_wrapper"
    ARTIFACTS_DIR = "artifacts"
    CONFIG_JSON = "config.json"
    PYTORCH_MODEL_DIR = "pytorch_output"
    PYFUNC_LOADER_MODULE = "mlflow.pyfunc.model"
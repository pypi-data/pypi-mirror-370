# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants related to MMEFT model."""


class MMEFTModelLiterals:
    """
    Literals related to MMEFT model code
    """
    TABULAR_CONFIG = "tabular_config"
    TEXT_CONFIG = "text_config"
    VISION_CONFIG = "vision_config"
    MODEL_TYPE = "model_type"


class MMEFTModelType:
    """
    Types of MMEFT models, based on the datatype of input
    """
    MMEFT_TABULAR_MODEL = "mmeft_tabular_model"
    MMEFT_TEXT_MODEL = "mmeft_text_model"
    MMEFT_VISION_MODEL = "mmeft_vision_model"


class MMEFTModelArchLiterals:
    """
    Literals used in MMEFT model architecture code.
    """
    BIAS = "bias"
    PARAMS = "params"
    WEIGHT = "weight"
    WEIGHT_DECAY = "weight_decay"


class MMEFTModelArchValues:
    """
    Constants used as values in MMEFT model architecture code.
    """
    NO_DECAY = 0.0
    DECAY = 1e-5

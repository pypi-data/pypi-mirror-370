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
File containing Multi modal Early Fusion Transformer model config
"""
import copy
import os
from typing import Dict, Any, Union
from transformers import PretrainedConfig

from azureml.acft.multimodal.components.model.mmeft.constants import MMEFTModelLiterals, MMEFTModelType
from azureml.acft.multimodal.components.constants.constants import MMEFTHyperParameterDefaults, ModelTypes


class AzuremlMMEarlyFusionTabularConfig(PretrainedConfig):
    """Config class to store the configuration of tabular embedder of Multi modal early fusion transformer."""
    model_type = MMEFTModelType.MMEFT_TABULAR_MODEL

    def __init__(self, d=MMEFTHyperParameterDefaults.EMBEDDING_SIZE, **kwargs):
        super().__init__(**kwargs)

        self.d = d

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)

        # get the tabular config dict if we are loading from AzuremlMMEarlyFusionConfig
        if config_dict.get(MMEFTModelLiterals.MODEL_TYPE) == ModelTypes.MMEFT:
            config_dict = config_dict[MMEFTModelLiterals.TABULAR_CONFIG]

        if MMEFTModelLiterals.MODEL_TYPE in config_dict and hasattr(cls, MMEFTModelLiterals.MODEL_TYPE) and config_dict[MMEFTModelLiterals.MODEL_TYPE] != cls.model_type:
            pass

        return cls.from_dict(config_dict, **kwargs)


class AzuremlMMEarlyFusionTextConfig(PretrainedConfig):
    """Config class to store the configuration of text embedder of Multi modal early fusion transformer."""
    model_type = MMEFTModelType.MMEFT_TEXT_MODEL

    def __init__(self, text_embedding_size=MMEFTHyperParameterDefaults.TEXT_EMBEDDING_SIZE, **kwargs):
        super().__init__(**kwargs)

        self.text_embedding_size = text_embedding_size

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)

        # get the text config dict if we are loading from AzuremlMMEarlyFusionConfig
        if config_dict.get(MMEFTModelLiterals.MODEL_TYPE) == ModelTypes.MMEFT:
            config_dict = config_dict[MMEFTModelLiterals.TEXT_CONFIG]

        if MMEFTModelLiterals.MODEL_TYPE in config_dict and hasattr(cls, MMEFTModelLiterals.MODEL_TYPE) and config_dict[MMEFTModelLiterals.MODEL_TYPE] != cls.model_type:
            pass

        return cls.from_dict(config_dict, **kwargs)


class AzuremlMMEarlyFusionVisionConfig(PretrainedConfig):
    """Config class to store the configuration of vision embedder of Multi modal early fusion transformer."""
    model_type = MMEFTModelType.MMEFT_VISION_MODEL

    def __init__(self, vision_embedding_size=MMEFTHyperParameterDefaults.VISION_EMBEDDING_SIZE, **kwargs):
        super().__init__(**kwargs)

        self.vision_embedding_size = vision_embedding_size

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)

        # get the vision config dict if we are loading from AzuremlMMEarlyFusionConfig
        if config_dict.get(MMEFTModelLiterals.MODEL_TYPE) == ModelTypes.MMEFT:
            config_dict = config_dict[MMEFTModelLiterals.VISION_CONFIG]

        if MMEFTModelLiterals.MODEL_TYPE in config_dict and \
                hasattr(cls, MMEFTModelLiterals.MODEL_TYPE) and \
                config_dict[MMEFTModelLiterals.MODEL_TYPE] != cls.model_type:
            pass

        return cls.from_dict(config_dict, **kwargs)


class AzuremlMMEarlyFusionConfig(PretrainedConfig):
    """Config class for Multi modal early fusion transformer model."""
    model_type = ModelTypes.MMEFT
    is_composition = True

    def __init__(
            self, tabular_config=None, text_config=None, vision_config=None,
            num_layers_of_transformers=MMEFTHyperParameterDefaults.NUM_TRANSFORMER_LAYERS,
            num_heads_in_the_transformer=MMEFTHyperParameterDefaults.NUM_TRANSFORMER_HEADS,
            transformer_dropout=MMEFTHyperParameterDefaults.TRANSFORMER_DROPOUT, prenorm=True,
            embedding_dropout=MMEFTHyperParameterDefaults.EMBEDDING_DROPOUT,
            num_numerical_features=None, categorical_cardinalities=None,
            num_classes=None, batch_size=8, num_text_cols=None, modes=None,
            **kwargs
    ):
        super().__init__(**kwargs)

        if tabular_config is None:
            # Init from defaults
            tabular_config = {}

        if text_config is None:
            # Init from defaults
            text_config = {}

        if vision_config is None:
            # Init from defaults
            vision_config = {}

        self.tabular_config = AzuremlMMEarlyFusionTabularConfig(**tabular_config)
        self.text_config = AzuremlMMEarlyFusionTextConfig(**text_config)
        self.vision_config = AzuremlMMEarlyFusionVisionConfig(**vision_config)

        self.num_layers_of_transformers = num_layers_of_transformers
        self.num_heads_in_the_transformer = num_heads_in_the_transformer
        self.transformer_dropout = transformer_dropout
        self.prenorm = prenorm
        self.embedding_dropout = embedding_dropout

        # Data specific args
        self.num_numerical_features = num_numerical_features
        self.categorical_cardinalities = categorical_cardinalities
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.num_text_cols = num_text_cols
        self.modes = modes

    @property
    def hidden_size(self):
        return self.tabular_config.d

    @classmethod
    def from_tabular_text_vision_configs(
        cls, tabular_config: AzuremlMMEarlyFusionTabularConfig, text_config: AzuremlMMEarlyFusionTextConfig,
        vision_config: AzuremlMMEarlyFusionVisionConfig, **kwargs
    ):
        cls(tabular_config=tabular_config, text_config=text_config, vision_config=vision_config, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output[MMEFTModelLiterals.TABULAR_CONFIG] = self.tabular_config.to_dict()
        output[MMEFTModelLiterals.TEXT_CONFIG] = self.text_config.to_dict()
        output[MMEFTModelLiterals.VISION_CONFIG] = self.vision_config.to_dict()
        output[MMEFTModelLiterals.MODEL_TYPE] = self.__class__.model_type
        return output

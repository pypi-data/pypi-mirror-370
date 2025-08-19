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
File containing HF tokenizer related functions
"""

from typing import Dict, Any

from transformers import CLIPTokenizer, PreTrainedTokenizerBase

from azureml.acft.common_components import get_logger_app

logger = get_logger_app(__name__)


class AzuremlCLIPTokenizer(CLIPTokenizer):

    @staticmethod
    def pre_init(hf_model_name_or_path: str) -> Dict[str, Any]:
        """Apply model adjustments before calling the Base tokenizer"""
        # ToDo: Check if pre_init needed for any use case
        model_specific_args = {}
        return model_specific_args

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> PreTrainedTokenizerBase:
        """
        All the model specific adjustments are defined in their respective task preprocessing files
        :param kwargs
            The kwargs can't contain arbitrary key-value pairs as most of the kwargs will be sent to tokenizer
            during initialization
        """

        apply_adjust = kwargs.pop("apply_adjust", True)
        model_specific_args = kwargs
        if apply_adjust:
            logger.info("Applying model adjustments")
            model_specific_args.update(AzuremlCLIPTokenizer.pre_init(hf_model_name_or_path))

        logger.info(f"Tokenizer initialized with args {model_specific_args}")
        logger.info(hf_model_name_or_path)
        try:
            # fast tokenizer
            tokenizer = super().from_pretrained(
                hf_model_name_or_path,
                use_fast=True,
                **model_specific_args,
            )
        except Exception as e:
            logger.warning(f"Fast tokenizer not supported: {e}")
            logger.info("Trying default tokenizer.")
            # slow tokenizer
            tokenizer = super(cls, cls).from_pretrained(
                hf_model_name_or_path,
                **model_specific_args,
            )
        logger.debug("Loaded tokenizer : {}".format(tokenizer))

        return tokenizer

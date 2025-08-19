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
common utilities
"""

import logging
import torch
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTSystemError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTSystemException
from azureml._common._error_definition.azureml_error import AzureMLError

logger = logging.getLogger(__name__)


def get_current_device() -> torch.device:
    """Get current cuda device
    :return: current device
    :rtype: torch.device
    """

    # check if GPU is available
    if torch.cuda.is_available():
        try:
            # get the current device index
            device_idx = torch.distributed.get_rank()
        except RuntimeError as ex:
            if "Default process group has not been initialized".lower() in str(ex).lower():
                device_idx = 0
            else:
                logger.error(str(ex))
                raise ACFTSystemException._with_error(
                    AzureMLError.create(ACFTSystemError, pii_safe_message=(
                        str(ex)
                    ))
                )
        return torch.device(type="cuda", index=device_idx)
    else:
        return torch.device(type="cpu")


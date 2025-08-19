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
File containing Multi modal Early Fusion Transformer model related functions
"""

import torch
import torch.nn as nn

from transformers import PreTrainedModel

from azureml.acft.multimodal.components.model.mmeft.constants import MMEFTModelArchLiterals, MMEFTModelArchValues
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_config import AzuremlMMEarlyFusionConfig
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_classifier.mm_fusion_classifier import \
    TransFusionClassifier



class AzuremlMMEarlyFusionModelForClassification(PreTrainedModel):
    config_class = AzuremlMMEarlyFusionConfig

    def __init__(self, config: AzuremlMMEarlyFusionConfig) -> None:
        super().__init__(config)
        self.arch = TransFusionClassifier(config)
        self.loss = nn.CrossEntropyLoss()

    def forward(self, tabular_data, text_data, image_data, labels):
        predicted_logits_fusion = self.arch((tabular_data, image_data, text_data))  # batch_size, num_classes
        if labels is not None:
            target = labels
            loss = self.loss(predicted_logits_fusion, target.squeeze(1))
        else:
            loss = None
        return loss, predicted_logits_fusion

    def _init_weights(self, module):
        """Initialize the weights"""
        pass


def create_optimizer_custom_func(model, learning_rate):
    # Code adopted from https://github.com/karpathy/nanoGPT/blob/177d5f7dc5f44d6f373cd7767c2a9259d740436e/model.py#L206

    decay = set()
    no_decay = set()
    whitelist_weight_modules = (torch.nn.Linear,)
    blacklist_weight_modules = (torch.nn.LayerNorm, torch.nn.Embedding)
    for mn, m in model.named_modules():
        for pn, p in m.named_parameters():
            fpn = '%s.%s' % (mn, pn) if mn else pn  # full param name
            # random note: because named_modules and named_parameters are recursive
            # we will see the same tensors p many many times. but doing it this way
            # allows us to know which parent module any tensor p belongs to...

            if (fpn.startswith('arch.transfusion_embedder.transformer_encoder')) or \
                    (fpn.startswith('arch.classification_head.')):
                if pn.endswith(MMEFTModelArchLiterals.BIAS):
                    # all biases will not be decayed
                    no_decay.add(fpn)
                elif pn.endswith(MMEFTModelArchLiterals.WEIGHT) and isinstance(m, whitelist_weight_modules):
                    # weights of whitelist modules will be weight decayed
                    decay.add(fpn)
                elif pn.endswith(MMEFTModelArchLiterals.WEIGHT) and isinstance(m, blacklist_weight_modules):
                    # weights of blacklist modules will NOT be weight decayed
                    no_decay.add(fpn)
            else:
                no_decay.add(fpn)

    # validate that we considered every parameter
    param_dict = {pn: p for pn, p in model.named_parameters()}
    inter_params = decay & no_decay
    union_params = decay | no_decay
    assert len(inter_params) == 0, "parameters %s made it into both decay/no_decay sets!" % (str(inter_params),)
    assert len(
        param_dict.keys() - union_params) == 0, "parameters %s were not separated into either decay/no_decay set!" \
                                                % (str(param_dict.keys() - union_params),)

    # create the pytorch optimizer object
    optim_groups = [
        {MMEFTModelArchLiterals.PARAMS: [param_dict[pn] for pn in sorted(list(decay))],
         MMEFTModelArchLiterals.WEIGHT_DECAY: MMEFTModelArchValues.DECAY},
        {MMEFTModelArchLiterals.PARAMS: [param_dict[pn] for pn in sorted(list(no_decay))],
         MMEFTModelArchLiterals.WEIGHT_DECAY: MMEFTModelArchValues.NO_DECAY},
    ]

    # https://pytorch.org/docs/stable/optim.html?highlight=optimizer#per-parameter-options
    optimizer = torch.optim.AdamW(optim_groups, lr=learning_rate)

    return optimizer

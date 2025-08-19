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

import torch
from torch import nn
from transformers import CLIPModel, PreTrainedModel, PretrainedConfig

# Make device agnostic code
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
HIDDEN_SIZE = 1024


class AzuremlAutoMLMultiModelConfig(PretrainedConfig):
    model_type = "multimodal-clip"

    def __init__(
            self,
            initializer_range=0.02,
            **kwargs
    ):
        self.initializer_range = initializer_range
        self.hidden_size = HIDDEN_SIZE
        self.model_name_or_path = kwargs.get("model_name_or_path")
        super().__init__(**kwargs)


class ClassHead(nn.Module):
    def __init__(self, num_labels):
        super().__init__()
        self.layer_1 = nn.Linear(in_features=HIDDEN_SIZE, out_features=num_labels)

    def forward(self, x):
        return self.layer_1(x)


class AzuremlAutoMLMultiModel(PreTrainedModel):
    config_class = AzuremlAutoMLMultiModelConfig

    def __init__(self, config):
        super().__init__(config)
        self.model = CLIPModel.from_pretrained(config.model_name_or_path)
        self.classification_head = ClassHead(config.num_labels)
        self.loss = nn.CrossEntropyLoss()

    def forward(self, **input):
        labels = input.pop("label", None)
        output = self.model(**input)
        combined_embedding = torch.cat([output.image_embeds, output.text_embeds], dim=1)
        pred = torch.softmax(self.classification_head(combined_embedding), -1).float()

        loss = None
        if labels is not None:
            pred = pred.to(self.device)
            labels = torch.tensor(labels).long().to(self.device)
            loss = self.loss(pred, labels)
        return {"loss": loss, "prediction": pred}

    def _init_weights(self, module):
        """Initialize the weights"""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

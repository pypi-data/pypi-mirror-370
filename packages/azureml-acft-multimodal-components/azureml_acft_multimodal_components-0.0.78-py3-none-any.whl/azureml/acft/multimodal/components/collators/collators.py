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
import numpy as np
import torch
from transformers.data.data_collator import default_data_collator
from azureml.acft.multimodal.components.constants.constants import ModelTypes, DatasetSplit


def get_collation_function(model_type):
    if model_type == ModelTypes.CLIP:
        return get_collation_function_for_clip
    elif model_type == ModelTypes.MMEFT:
        return get_collation_function_for_mmeft


def get_collation_function_for_mmeft(self):
    def collation_fn(examples):
        if self.text_data_present():
            encoding_list = []
            for example in examples:
                text_data = [example[text_column] for text_column in self.text_columns]
                text_encoding = self.text_tokenizer(text_data, padding='max_length', truncation=True,
                                                    max_length=256, return_tensors='pt')
                text_encoding.to(self.device)
                encoding_list.append(text_encoding)
            text_tensors = default_data_collator(encoding_list)
        else:
            text_tensors = torch.zeros(size=(len(examples), 2), device=self.device)

        if self.tabular_data_present():
            tabular_tensors = torch.tensor([
                [example[column] if example[column] is not None else float('nan')
                 for column in self.numerical_columns + self.categorical_columns]
                for example in examples], device=self.device)
        else:
            tabular_tensors = torch.zeros(size=(len(examples), 2), device=self.device)

        if self.image_data_present():
            # transformed data
            image_data = torch.stack(
                [example[self.image_column_name] if example[self.image_column_name] is not None
                 else torch.zeros((3, 224, 224)) for example in examples]
            )
            image_data = image_data.to(device=self.device)
            missing_mask_data = torch.tensor(
                [0.0 if example[self.image_column_name] is not None else 1.0
                 for example in examples], device=self.device
            )
            image_tensors = (image_data, missing_mask_data)
        else:
            image_tensors = torch.zeros(size=(len(examples), 2), device=self.device)

        labels_tensor = None
        if self.data_split != DatasetSplit.TEST:
            if self.is_multilabel:
                labels = np.zeros((len(examples), len(self.label2id)), dtype=np.float64)
                for idx, example in enumerate(examples):
                    for label_id in example[self.label_column]:
                        labels[idx][label_id] = 1
                labels_tensor = torch.tensor(labels, dtype=torch.float, device=self.device)
            else:
                labels = [[example[self.label_column]] for example in examples]
                labels_tensor = torch.tensor(labels, device=self.device).long()

        return {
            "tabular_data": tabular_tensors,
            "text_data": text_tensors,
            "image_data": image_tensors,
            "labels": labels_tensor
        }

    return collation_fn


def get_collation_function_for_clip(self):
    def collation_fn(examples):
        images, texts = [], []
        for example in examples:
            images.append(example[self.image_column_name])
            texts.append(example[self.text_columns[0]])
        input_model = self.processor(text=texts, images=images, return_tensors="pt", padding='max_length',
                                     truncation=True, max_length=77)
        input_model.to(self.device)
        if self.label_column is not None and self.data_split != DatasetSplit.TEST:
            input_model['label'] = torch.Tensor(
                [example[self.label_column] for example in examples], device=self.device
            ).long()
        return input_model

    return collation_fn

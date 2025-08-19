# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Standard libraries
import torch
import torch.nn as nn
from torch import Tensor
import math

from azureml.acft.multimodal.components.utils.common_utils import get_current_device


class NumericalTokenizer(nn.Module):
    # https://arxiv.org/pdf/2106.11959.pdf - Figure 2
    # d: Desired dimensionality of the embeddings for a feature. All features, cats and nums are embedded to d size
    # num_numerical_features : Number of numerical features
    def __init__(self, d, num_numerical_features):
        super().__init__()
        self.W = nn.Parameter(Tensor(num_numerical_features, d))
        self.b = nn.Parameter(Tensor(num_numerical_features, d))

        self.W_missing = nn.Parameter(Tensor(num_numerical_features, d))

        # Used in the paper "Revisiting Deep Learning Models for Tabular Data";
        # https://github.com/pytorch/pytorch/blob/f4099af1e99c0715f6ea488619378aadf68ea91f/torch/nn/modules/linear.py#L103
        # Note on Kaiming :
        """
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(in_features), 1/sqrt(in_features)). For details, see
        # https://github.com/pytorch/pytorch/issues/57109
        """
        nn.init.uniform_(self.b, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))
        nn.init.uniform_(self.W, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))

        nn.init.uniform_(self.W_missing, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))

    def forward(self, x, bias=True):

        # Handle missing values here
        missing_mask = torch.isnan(x)
        x = x.masked_fill_(missing_mask, 1.0)
        one_for_present_zero_for_missing = (~missing_mask).float()  # this has same dimension as x
        zero_for_present_one_for_missing = missing_mask.float()  # this has same dimension as x
        ####

        weight_multiplier = self.W.unsqueeze(0) * one_for_present_zero_for_missing.unsqueeze(
            dim=-1) + self.W_missing.unsqueeze(0) * zero_for_present_one_for_missing.unsqueeze(dim=-1)

        if bias:
            return weight_multiplier * x.unsqueeze(dim=-1) + self.b.unsqueeze(0)
        else:
            return weight_multiplier * x.unsqueeze(dim=-1)


class CategoricalTokenizer(nn.Module):
    # https://arxiv.org/pdf/2106.11959.pdf - Figure 2
    # d: Desired dimensionality of the embeddings for a feature. All features, cats and nums are embedded to d size
    # num_numerical_features : Number of numerical features
    def __init__(self, d, cardinalities):
        super().__init__()
        self.num_categorical_features = len(cardinalities)
        self.d = d
        embeddings = []
        for card in cardinalities:
            tmp = nn.Embedding(card, d)
            nn.init.uniform_(tmp.weight, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))
            embeddings.append(tmp)

        self.embedding_list = nn.ModuleList(embeddings)
        self.b = nn.Parameter(Tensor(self.num_categorical_features, d))
        nn.init.uniform_(self.b, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))

        # Used in the paper "Revisiting Deep Learning Models for Tabular Data";
        # https://github.com/pytorch/pytorch/blob/f4099af1e99c0715f6ea488619378aadf68ea91f/torch/nn/modules/linear.py#L103
        # Note on Kaiming :
        """
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(in_features), 1/sqrt(in_features)). For details, see
        # https://github.com/pytorch/pytorch/issues/57109
        """

    def forward(self, x, bias=True):
        batch_size = x.shape[0]
        # print(x.shape)
        # print(self.num_categorical_features)
        assert x.shape[1] == self.num_categorical_features
        val = torch.hstack([self.embedding_list[i](x[:, i]) for i in range(self.num_categorical_features)]) \
            .reshape(shape=(batch_size, self.num_categorical_features, self.d))
        if bias:
            val = val + self.b.unsqueeze(0)
        return val


class CLSTokenAndStacking(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.d = d
        self.weight = nn.Parameter(Tensor(self.d))
        nn.init.uniform_(self.weight, a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))

    def forward(self, tokenized_numericals, tokenized_categoricals):
        batch_size = tokenized_numericals.shape[0]
        self.weight.expand((batch_size, self.d))
        return torch.hstack([tokenized_numericals, tokenized_categoricals])


class FeatureTokenizer(nn.Module):

    # https://arxiv.org/pdf/2106.11959.pdf - Figure 2

    # d: Desired dimensionality of the embeddings for a feature. All features, cats and nums are embedded to d size
    # num_numerical_features : Number of numerical features
    # num_categorical_features : Number of categorical features
    def __init__(self, d, num_numerical_features, categorical_cardinalities):
        super().__init__()
        self.d = d
        self.categorical_tokenizer = self.numerical_tokenizer = None
        if num_numerical_features and num_numerical_features > 0:
            self.numerical_tokenizer = NumericalTokenizer(d=self.d, num_numerical_features=num_numerical_features)
        if categorical_cardinalities and len(categorical_cardinalities) > 0:
            self.categorical_tokenizer = CategoricalTokenizer(d=self.d, cardinalities=categorical_cardinalities)
        self.num_numerical_features = num_numerical_features
        self.num_categorical_features = len(categorical_cardinalities)
        self.device = get_current_device()

    def forward(self, x):
        # print(x[:,self.num_numerical_features:].long())
        tokenized_numericals = torch.tensor([])
        tokenized_categoricals = torch.tensor([])
        if self.numerical_tokenizer:
            tokenized_numericals = self.numerical_tokenizer(x[:, 0:self.num_numerical_features])
        if self.categorical_tokenizer:
            tokenized_categoricals = self.categorical_tokenizer(x[:, self.num_numerical_features:].long())

        return tokenized_numericals.to(self.device), tokenized_categoricals.to(self.device)

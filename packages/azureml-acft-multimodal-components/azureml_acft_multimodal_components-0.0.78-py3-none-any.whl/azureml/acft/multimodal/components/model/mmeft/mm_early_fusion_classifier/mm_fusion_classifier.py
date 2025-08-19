# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MM Early Fusion Classifier model definition"""

from torch import Tensor
from torchvision import models

import torch
import math
import torch.nn as nn

from .ft_transformer import FTTransformerEmbedder

from .attention import TransformerEncoder

from .ft_transformer import ClassificationHead

from azureml.acft.multimodal.components.constants.constants import DataMode


class CLSTokenAndStackingForFusor(nn.Module):
    def __init__(self, total_mm_embedding_size):
        super().__init__()
        self.total_mm_embedding_size = total_mm_embedding_size
        self.weight = nn.Parameter(Tensor(self.total_mm_embedding_size))
        nn.init.uniform_(
            self.weight, a=-(1 / math.sqrt(total_mm_embedding_size)),
            b=(1 / math.sqrt(total_mm_embedding_size)))

    def forward(self, tabular_embeddings, vision_embeddings, text_embeddings):
        tostack = []
        tostack_final = []
        if tabular_embeddings is not None:
            tostack.append(tabular_embeddings)
        if vision_embeddings is not None:
            tostack.append(vision_embeddings)

        if text_embeddings is not None:
            tostack_final = tostack + text_embeddings
        else:
            tostack_final = tostack

        return torch.hstack(tostack_final)


class TextEmbedder(nn.Module):
    def __init__(self, config, batch_size, num_text_cols) -> None:
        super().__init__()
        self.batch_size = batch_size
        self.num_text_cols = num_text_cols
        self.pretrained_embedding_size_text = config.text_embedding_size
        from transformers import BertModel, BertConfig
        self.model = BertModel(config=BertConfig())
        # self.model = BertModel.from_pretrained("bert-base-uncased")

    def forward(self, x):
        output = self.model(**x)
        return output[0][:, 0, :]


class ResNetEmbedder(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.model = self.initialize_model(use_pretrained=False)[0]

        d = config.vision_embedding_size
        self.special_embedding_missing = nn.Parameter(Tensor(d))
        nn.init.uniform_(self.special_embedding_missing,
                         a=-(1 / math.sqrt(d)), b=(1 / math.sqrt(d)))

        self.embedding_size = config.vision_embedding_size

    # Adopted from https://pytorch.org/tutorials/beginner/finetuning_torchvision_models_tutorial.html
    def initialize_model(
            self, model_name='resnet', feature_extract=False,
            use_pretrained=True):
        # Initialize these variables which will be set in this if statement. Each of these
        #   variables is model specific.

        def set_parameter_requires_grad(model, feature_extracting):
            if feature_extracting:
                for param in model.parameters():
                    param.requires_grad = False

        model_ft = None
        input_size = 0

        if model_name == "resnet":
            """ Resnet18
            """
            model_ft = models.resnet18(pretrained=use_pretrained)
            set_parameter_requires_grad(model_ft, feature_extract)
            input_size = 224
        else:
            print("Invalid model name, exiting...")
            exit()

        return model_ft, input_size

    def forward(self, x):
        inp, mask = x

        mask = mask.flatten()

        batch_size = inp.shape[0]
        special_embedding_missing_expanded = self.special_embedding_missing.expand(
            (batch_size, self.embedding_size))

        return (self.model(inp) * (1-mask.unsqueeze(-1))) + (special_embedding_missing_expanded * mask.unsqueeze(-1))


class TransFusionEmbedder(nn.Module):
    def __init__(
        self, config, num_numerical_features, categorical_cardinalities, num_classes,
        batch_size, num_text_cols, modes
    ) -> None:
        super().__init__()

        d = config.tabular_config.d
        # assert d == tabular_embedding_size
        self.tabular_embedder = FTTransformerEmbedder(
            d=d, num_numerical_features=num_numerical_features,
            categorical_cardinalities=categorical_cardinalities,
            num_classes=num_classes)
        self.vision_embedder = ResNetEmbedder(config=config.vision_config)
        self.text_embedder = TextEmbedder(config=config.text_config, batch_size=batch_size,
                                          num_text_cols=num_text_cols)

        self.num_numerical_features = num_numerical_features
        self.num_categorical_features = len(categorical_cardinalities)
        self.common_embedding_size = d
        self.tabular_embedding_size = config.tabular_config.d
        self.vision_embedding_size = config.vision_config.vision_embedding_size
        self.text_embedding_size = config.text_config.text_embedding_size
        self.transformer_dropout = config.transformer_dropout
        self.embedding_dropout = config.embedding_dropout
        self.modes = modes

        self.cls_and_stacker = CLSTokenAndStackingForFusor(
            total_mm_embedding_size=self.common_embedding_size)

        self.transformer_encoder = TransformerEncoder(
            num_layers=config.num_layers_of_transformers,  # Number of Encoder Blocks
            # size of the input embeddings of an element of a sequence
            input_dim=self.common_embedding_size,
            # 4 taken from Vaswani https://arxiv.org/pdf/1706.03762.pdf -- Section 3.3 -- 2048/512 = 4
            dim_feedforward=int(4 * self.common_embedding_size),
            num_heads=config.num_heads_in_the_transformer,
            dropout=self.transformer_dropout,
            pre_norm=config.prenorm
        )

        embedding_dropout = self.embedding_dropout
        self.dropout_tabular = nn.Dropout(embedding_dropout)
        self.dropout_vision = nn.Dropout(embedding_dropout)

        self.dropout_text = nn.ModuleList(
            [nn.Dropout(embedding_dropout) for k in range(num_text_cols)])

        self.vision_embedding_bias = nn.Parameter(
            Tensor(self.common_embedding_size))
        self.text_embedding_bias = nn.ParameterList(
            [nn.Parameter(Tensor(self.common_embedding_size))
             for k in range(num_text_cols)])

        self.lin_tabular = nn.Linear(
            self.tabular_embedding_size, self.common_embedding_size)
        self.lin_vision = nn.Linear(
            self.vision_embedding_size, self.common_embedding_size, bias=False)
        self.num_text_cols = num_text_cols

        self.lin_text = nn.ModuleList(
            [nn.Linear(
                self.text_embedding_size, self.common_embedding_size,
                bias=False) for k in range(num_text_cols)])

        nn.init.uniform_(
            self.vision_embedding_bias, a=-
            (1 / math.sqrt(self.common_embedding_size)),
            b=(1 / math.sqrt(self.common_embedding_size)))

        for k in range(num_text_cols):
            nn.init.uniform_(
                self.text_embedding_bias[k],
                a=-(1 / math.sqrt(self.common_embedding_size)),
                b=(1 / math.sqrt(self.common_embedding_size)))

    def forward(self, x):
        tabular_inp, vision_input, text_input = x

        # Downsample to common embedding size i.e. d --> Add Bias --> Dropout 0.1

        if DataMode.IMAGE in self.modes:
            vision_input = self.dropout_vision(self.lin_vision(self.vision_embedder(
                vision_input)) + self.vision_embedding_bias)  # batch_size, 32
        else:
            vision_input = None

        if DataMode.TEXT in self.modes:
            text_embeddings_intermediate = []

            for k in range(
                    self.num_text_cols):  # Todo: better way? - #Purposefully not batching?
                inp_new = {}
                inp_new['input_ids'] = text_input['input_ids'][:, k, :]
                inp_new['token_type_ids'] = text_input['token_type_ids'][:, k, :]
                inp_new['attention_mask'] = text_input['attention_mask'][:, k, :]
                text_embeddings_intermediate.append(
                    self.text_embedder(inp_new))

            text_embeddings = [
                txt_dropout(downsampler(e) + bias) for downsampler, bias,
                txt_dropout,
                e
                in
                zip(
                    self.lin_text, self.text_embedding_bias, self.dropout_text,
                    text_embeddings_intermediate)]
        else:
            text_embeddings = None

        if DataMode.TABULAR in self.modes:
            # Dropout 0.1 (no downsampling here)
            # batch_size, num_tabular_features, d = 32; already has a bias
            tabular_inp = self.dropout_tabular(
                self.tabular_embedder(tabular_inp))
        else:
            tabular_inp = None

        if vision_input is not None:
            vision_input = vision_input.unsqueeze(dim=1)  # batch_size, 1 , 32

        if text_embeddings is not None:
            text_embeddings_unsqueezed = [
                r.unsqueeze(dim=1) for r in text_embeddings]
        else:
            text_embeddings_unsqueezed = None

        final_attention = self.transformer_encoder(self.cls_and_stacker(
            tabular_inp, vision_input, text_embeddings_unsqueezed))

        final_meaned_embedding = final_attention.mean(dim=1)

        return final_meaned_embedding


class TransFusionClassifier(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.transfusion_embedder = TransFusionEmbedder(
            config=config, num_numerical_features=config.num_numerical_features,
            categorical_cardinalities=config.categorical_cardinalities, num_classes=config.num_classes,
            batch_size=config.batch_size, num_text_cols=config.num_text_cols, modes=config.modes
        )
        self.classification_head = ClassificationHead(d=config.tabular_config.d, num_classes=config.num_classes)

    def forward(self, x):
        embedding = self.transfusion_embedder(x)
        return self.classification_head(embedding)

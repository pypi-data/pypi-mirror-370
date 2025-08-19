# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Standard libraries
# Plotting


# PyTorch


import torch.nn as nn

from .attention import TransformerEncoder

from .feature_tokenizer import CLSTokenAndStacking, FeatureTokenizer

class TabularEmbedding(nn.Module):
    def __init__(self, d) -> None:
        super().__init__()

        # Layers to apply in between the main layers
        self.norm1 = nn.LayerNorm(d)
        self.relu = nn.GELU()
        self.lin = nn.Linear(d, d)

    
    def forward(self, x):
        batch_size, num_sequences, d = x.size()
        #CLS Token output - CLS is always the zeroth sequence:
        cls_embedding = x[:,0,:] #shape = batch_size, d
        return self.lin(self.relu(self.norm1(cls_embedding)))


class ClassificationHead(nn.Module):
    def __init__(self, d, num_classes) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(d)
        self.affine_1 = nn.Linear(d, 2*d)
        self.activation = nn.GELU()
        self.affine_2 = nn.Linear(2*d, num_classes)

    
    def forward(self, x):
        x = self.norm(x)
        x = self.affine_1(x)
        x = self.activation(x)
        x = self.affine_2(x)
        return x


class FTTransformerClassifier(nn.Module):
    def __init__(self, d, num_numerical_features, categorical_cardinalities: list, num_classes):
        super().__init__()
        self.d = d  # Size of embeddings of the cats and nums features -  from the original paper
        self.classification_head = ClassificationHead(d=d, num_classes=num_classes)
        self.tabular_embedder = TabularEmbedding(d=d)
        self.transformer_encoder = TransformerEncoder(
            num_layers=3,  # Number of Encoder Blocks
            input_dim=d,  # size of the input embeddings of an element of a sequence
            dim_feedforward=2 * d,
            num_heads=1,
            dropout=0.01,
        )
        self.cls_and_stacker = CLSTokenAndStacking(d=d)
        self.ft = FeatureTokenizer(d=d, num_numerical_features=num_numerical_features,
                                   categorical_cardinalities=categorical_cardinalities)
    
    def forward(self, x):
        batch_size, num_features = x.size()
        numericals, categoricals = self.ft(x)
        out = self.cls_and_stacker(tokenized_numericals = numericals, tokenized_categoricals=categoricals)
        transout = self.transformer_encoder(out)
        joint_embedding = self.tabular_embedder(transout)
        return self.classification_head(joint_embedding)

class FTTransformerEmbedder(nn.Module):
    def __init__(self, d, num_numerical_features, categorical_cardinalities:list, num_classes):
        super().__init__()
        self.d = d #Size of embeddings of the cats and nums features -  from the original paper
        self.classification_head = ClassificationHead(d=d, num_classes=num_classes)
        self.tabular_embedder = TabularEmbedding(d=d)
        self.cls_and_stacker = CLSTokenAndStacking(d=d)
        self.ft = FeatureTokenizer(d=d,
                                   num_numerical_features=num_numerical_features,
                                   categorical_cardinalities=categorical_cardinalities)
    
    def forward(self, x):
        batch_size, num_features = x.size()
        numericals, categoricals = self.ft(x)
        return self.cls_and_stacker(tokenized_numericals=numericals, tokenized_categoricals=categoricals)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

#Adapted from Vaswani et al [Attention is all you need]. Modifications done on top of code adapted from https://pytorch-lightning.readthedocs.io/en/stable/notebooks/course_UvA-DL/05-transformers-and-MH-attention.html



import torch
import math
import torch.nn.functional as F

import torch.nn as nn

def scaled_dot_product(q, k, v, mask=None):
    d_k = q.size()[-1]
    attn_logits = torch.matmul(q, k.transpose(-2, -1))
    attn_logits = attn_logits / math.sqrt(d_k)
    if mask is not None:
        attn_logits = attn_logits.masked_fill(mask == 0, -9e15)
    attention = F.softmax(attn_logits, dim=-1)
    values = torch.matmul(attention, v)
    return values, attention



class MultiheadAttention(nn.Module):
    def __init__(self, input_dim, embed_dim, num_heads):
        super().__init__()
        assert embed_dim % num_heads == 0, "Embedding dimension must be 0 modulo number of heads."

        assert input_dim == embed_dim

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        # Stack all weight matrices 1...h together for efficiency
        # Note that in many implementations you see "bias=False" which is optional
        self.qkv_proj = nn.Linear(input_dim, 3 * embed_dim)
        self.o_proj = nn.Linear(embed_dim, embed_dim)

        self._reset_parameters()

    def _reset_parameters(self):
        # Original Transformer initialization, see PyTorch documentation
        nn.init.xavier_uniform_(self.qkv_proj.weight)
        self.qkv_proj.bias.data.fill_(0)
        nn.init.xavier_uniform_(self.o_proj.weight)
        self.o_proj.bias.data.fill_(0)

    def forward(self, x, mask=None, return_attention=False):
        batch_size, seq_length, embed_dim = x.size()
        qkv = self.qkv_proj(x)

        # Separate Q, K, V from linear output
        qkv = qkv.reshape(batch_size, seq_length, self.num_heads, 3 * self.head_dim)
        qkv = qkv.permute(0, 2, 1, 3)  # [Batch, Head, SeqLen, Dims]
        q, k, v = qkv.chunk(3, dim=-1)

        # Determine value outputs
        values, attention = scaled_dot_product(q, k, v, mask=mask)
        values = values.permute(0, 2, 1, 3)  # [Batch, SeqLen, Head, Dims]
        values = values.reshape(batch_size, seq_length, embed_dim)
        o = self.o_proj(values)

        if return_attention:
            return o, attention
        else:
            return o


class EncoderBlock(nn.Module):
    def __init__(self, input_dim, num_heads, dim_feedforward, dropout, pre_norm):
        """
        Args:
            input_dim: Dimensionality of the input
            num_heads: Number of heads to use in the attention block
            dim_feedforward: Dimensionality of the hidden layer in the MLP
            dropout: Dropout probability to use in the dropout layers
        """
        super().__init__()

        # Attention layer
        self.self_attn = MultiheadAttention(input_dim, input_dim, num_heads)

        # Two-layer MLP
        self.linear_net = nn.Sequential(
            nn.Linear(input_dim, dim_feedforward),
            nn.GELU(),
            nn.Dropout(dropout), 
            nn.Linear(dim_feedforward, input_dim),
        )

        # Layers to apply in between the main layers
        self.norm1 = nn.LayerNorm(input_dim)
        self.norm2 = nn.LayerNorm(input_dim)
        self.residual_dropout = nn.Dropout(dropout) 
        self.attn_dropout = nn.Dropout(dropout) 
        self.pre_norm = pre_norm


        # def forward(self, x, mask=None, layer_norm_enabled = True):

    def forward(self, x, mask=None):

        if not self.pre_norm:
            #Original Forward of the Vaswani Transformer:
            # Attention part
            attn_out = self.self_attn(x, mask=None)
            x = x + self.attn_dropout(attn_out)
            x = self.norm1(x)

            # MLP part
            linear_out = self.linear_net(x)
            x = x + self.residual_dropout(linear_out)
            x = self.norm2(x)

            return x
        else:
            #Inspired by NanoGPT, Karpathy et al. https://github.com/karpathy/nanoGPT/blob/177d5f7dc5f44d6f373cd7767c2a9259d740436e/model.py#L88
            #Follows Fig 2b = https://arxiv.org/pdf/2106.11959.pdf
            #sub-layer is self attention + dropout
            # Attention part
            x = x + self.attn_dropout(self.self_attn(self.norm1(x), mask=None)) ## "self.dropout(attn_out)"" is the sub layer -- https://arxiv.org/pdf/1706.03762.pdf --  We apply dropout [33] to the output of each sub-layer, before it is added to the sub-layer input and normalized.
        
            #MLP part
            x = x + self.residual_dropout(self.linear_net(self.norm2(x)))

            return x


class TransformerEncoder(nn.Module):
    def __init__(self, num_layers, **block_args):
        super().__init__()
        self.layers = nn.ModuleList([EncoderBlock(**block_args) for _ in range(num_layers)])

    def forward(self, x, mask=None):
        for layer in self.layers:
            x = layer(x, mask=mask)
        return x

    def get_attention_maps(self, x, mask=None):
        attention_maps = []
        for layer in self.layers:
            _, attn_map = layer.self_attn(x, mask=mask, return_attention=True)
            attention_maps.append(attn_map)
            x = layer(x)
        return attention_maps


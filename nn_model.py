# -*- coding: utf-8 -*-
"""nn_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uIukKtO6rlD8CyaEpKgRMcpe-VSqLDDJ
"""

import torch.nn as nn
import torch.nn.functional as F
import torch

class Classifier(nn.Module):

  def __init__(self, dist_layer_size=128):
    super(Classifier, self).__init__()
    self.fc = nn.Sequential(
        nn.Linear(dist_layer_size, 1),
        nn.Sigmoid()
    )

  def forward(self, pooler_embedding1, pooler_embedding2):
    output1 = pooler_embedding1
    output2 = pooler_embedding2
    dist = torch.abs(output1 - output2)
    return self.fc(dist)

class ConvEmbed(nn.Module):

  def __init__(self, output_size=128, num_filters=100, embedding_dim=768, 
               kernel_sizes=[3, 4, 6], drop_prob=0.5):
    super(ConvEmbed, self).__init__()
    self.convs_1d = nn.ModuleList(
        [nn.Conv2d(1, num_filters, (k, embedding_dim)) for k in kernel_sizes]
        )
    self.fc = nn.Linear(len(kernel_sizes) * num_filters, output_size) 
    self.dropout = nn.Dropout(drop_prob)
    self.batchnorm2d = nn.BatchNorm2d(num_filters)

  def conv_and_pool(self, x, conv):
    x = self.batchnorm2d(conv(x))
    x =  F.relu(x).squeeze(3)
    x_max = F.max_pool1d(x, x.size(2)).squeeze(2)
    return x_max

  def forward(self, word_embedding):
    conv_results = [self.conv_and_pool(word_embedding, conv) for conv in self.convs_1d]
    x = torch.cat(conv_results, 1)
    x = self.dropout(x)
    return self.fc(x)
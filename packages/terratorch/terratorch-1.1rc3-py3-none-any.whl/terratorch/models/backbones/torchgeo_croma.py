# reference torchgeo https://torchgeo.readthedocs.io/en/stable/_modules/torchgeo/models/vit.html

from torchgeo.models.croma import CROMA
import logging
from collections.abc import Callable
from functools import partial
import huggingface_hub
import torch.nn as nn
from typing import List
import huggingface_hub
from torchvision.models._api import Weights, WeightsEnum
import torch
from terratorch.models.backbones.select_patch_embed_weights import select_patch_embed_weights

from terratorch.registry import TERRATORCH_BACKBONE_REGISTRY

class CROMAWrapper(nn.Module):

    def __init__(self, croma_model, croma_meta, weights=None, out_indices=None) -> None:
        """
        Args:
            dofa_model (DOFA): The decoder module to be wrapped.
            weights ()
        """
        super().__init__()
        self.croma_model = croma_model
        self.weights = weights
        self.out_channels = [x['num_chs'] for x in self.croma_model.feature_info]
        self.croma_meta = croma_meta

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        return self.croma_model.forward_intermediates(x, intermediates_only=True)

croma_base_config = {
                      "modalities": ['sar', 'optical'],
                      "encoder_dim": 768,
                      "encoder_depth": 12,
                      "num_heads": 16,
                      "patch_size": 8,
                      "image_size": 120,
                    }

croma_large_config = {
                      "modalities": ['sar', 'optical'],
                      "encoder_dim": 768,
                      "encoder_depth": 12,
                      "num_heads": 16,
                      "patch_size": 8,
                      "image_size": 120,
                    }

@TERRATORCH_BACKBONE_REGISTRY.register
def croma_base(model_bands=None, pretrained: bool = False, ckpt_data: bool = None):
  model = CROMA(**croma_base_config)
  return model 

@TERRATORCH_BACKBONE_REGISTRY.register
def croma_large(model_bands=None, pretrained: bool = False, ckpt_data: str = None):
  model = CROMA(**croma_large_config)
  return model 


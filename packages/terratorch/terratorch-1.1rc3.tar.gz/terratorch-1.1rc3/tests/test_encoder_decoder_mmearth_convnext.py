# Copyright contributors to the Terratorch project
import gc
import importlib

import pytest
import torch

from terratorch.models import EncoderDecoderFactory
from terratorch.models.backbones.prithvi_vit import PRETRAINED_BANDS
from terratorch.models.model import AuxiliaryHead

NUM_CHANNELS = 6
NUM_CLASSES = 10
EXPECTED_SEGMENTATION_OUTPUT_SHAPE = (1, NUM_CLASSES, 224, 224)
EXPECTED_REGRESSION_OUTPUT_SHAPE = (1, 224, 224)
EXPECTED_CLASSIFICATION_OUTPUT_SHAPE = (1, NUM_CLASSES)

PIXELWISE_TASK_EXPECTED_OUTPUT = [
    ("regression", EXPECTED_REGRESSION_OUTPUT_SHAPE),
    ("segmentation", EXPECTED_SEGMENTATION_OUTPUT_SHAPE),
]

VIT_UPERNET_NECK = [
    {"name": "SelectIndices", "indices": [0, 1, 2, 3]},
    {"name": "ReshapeTokensToImage"},
    {"name": "LearnedInterpolateToPyramidal"},
]

PRETRAINED_BANDS = ["RED", "GREEN", "BLUE", "NIR_NARROW", "SWIR_1", "SWIR_2"]

@pytest.fixture(scope="session")
def model_factory() -> EncoderDecoderFactory:
    return EncoderDecoderFactory()


@pytest.fixture(scope="session")
def model_input() -> torch.Tensor:
    return torch.ones((1, NUM_CHANNELS, 224, 224))


backbones = ["convnextv2_base"]
pretrained = [False, True]
@pytest.mark.parametrize("backbone", backbones)
@pytest.mark.parametrize("backbone_pretrained", pretrained)
def test_create_classification_model_resnet(backbone, model_factory: EncoderDecoderFactory, model_input, backbone_pretrained):
    model = model_factory.build_model(
        "classification",
        backbone=backbone,
        decoder="IdentityDecoder",
        backbone_in_chans=len(PRETRAINED_BANDS),
        backbone_pretrained=backbone_pretrained,
        num_classes=NUM_CLASSES,
    )
    model.eval()

    with torch.no_grad():
        assert model(model_input).output.shape == EXPECTED_CLASSIFICATION_OUTPUT_SHAPE

    gc.collect()

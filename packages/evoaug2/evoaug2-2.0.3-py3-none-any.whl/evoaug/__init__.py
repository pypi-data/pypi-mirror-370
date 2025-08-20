"""
EvoAug2: Evolution-inspired sequence augmentations as a DataLoader

This package provides evolution-inspired data augmentations for genomic sequences
and a simple way to use them with any PyTorch model via a drop-in DataLoader.
"""

from .evoaug import RobustLoader, AugmentedGenomicDataset
from . import augment

__version__ = "2.0.0"
__all__ = ["RobustLoader", "AugmentedGenomicDataset", "augment"] 
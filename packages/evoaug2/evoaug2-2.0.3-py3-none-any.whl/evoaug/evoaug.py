"""
EvoAug2: PyTorch DataLoader implementation of EvoAug functionality.

This module provides the same augmentation capabilities as RobustModel but
as a standalone PyTorch DataLoader that can be used with any model.

The RobustLoader inherits from DataLoader and can be used directly in
PyTorch Lightning DataModules or vanilla PyTorch training loops.

Classes
-------
AugmentedGenomicDataset
    Dataset wrapper that applies EvoAug augmentations on-the-fly.
RobustLoader
    DataLoader with built-in EvoAug augmentations.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Optional, Tuple, Union
from evoaug.augment import AugmentBase


class AugmentedGenomicDataset(Dataset):
    """
    PyTorch Dataset that applies EvoAug-style augmentations to genomic sequences.
    
    This dataset wraps an existing dataset and applies augmentations on-the-fly
    during training, while optionally disabling them for validation/finetuning.
    
    Parameters
    ----------
    base_dataset : torch.utils.data.Dataset
        The underlying dataset that provides (sequence, target) pairs.
    augment_list : List[AugmentBase], optional
        List of data augmentations to apply. Defaults to empty list.
    max_augs_per_seq : int, optional
        Maximum number of augmentations to apply per sequence. Defaults to 0.
    hard_aug : bool, optional
        If True, always apply exactly max_augs_per_seq augmentations.
        If False, randomly sample 1 to max_augs_per_seq augmentations. Defaults to True.
    apply_augmentations : bool, optional
        Whether to apply augmentations. Can be toggled for finetuning. Defaults to True.
        
    Notes
    -----
    - The dataset automatically detects the maximum insertion length from augmentations
    - Augmentations can be enabled/disabled at runtime using enable_augmentations()
      and disable_augmentations() methods
    - Each sequence receives a different random combination of augmentations
    """
    
    def __init__(self, 
                 base_dataset: Dataset,
                 augment_list: List[AugmentBase] = [],
                 max_augs_per_seq: int = 0,
                 hard_aug: bool = True,
                 apply_augmentations: bool = True):
        
        self.base_dataset = base_dataset
        self.augment_list = augment_list
        self.max_augs_per_seq = min(max_augs_per_seq, len(augment_list))
        self.hard_aug = hard_aug
        self.apply_augmentations = apply_augmentations
        self.max_num_aug = len(augment_list)
        self.insert_max = self._get_insert_max()
        
    def __len__(self):
        """Return the number of samples in the dataset.
        
        Returns
        -------
        int
            Number of samples in the base dataset.
        """
        return len(self.base_dataset)
    
    def __getitem__(self, idx):
        """Get a single sample from the dataset.
        
        Parameters
        ----------
        idx : int
            Index of the sample to retrieve.
            
        Returns
        -------
        torch.Tensor or tuple
            If target exists: (augmented_sequence, target)
            If no target: augmented_sequence
            
        Notes
        -----
        - Sequences are augmented on-the-fly if augmentations are enabled
        - Augmentations preserve the original sequence length L
        - Each call may produce different augmentations due to randomness
        """
        # Get the original data
        data = self.base_dataset[idx]
        
        # Handle different data formats
        if isinstance(data, (tuple, list)) and len(data) >= 2:
            sequence, target = data[0], data[1]
        else:
            sequence = data
            target = None
            
        # Apply augmentations if enabled
        if self.apply_augmentations and self.augment_list:
            sequence = self._apply_augmentations(sequence)
        # elif self.insert_max > 0:
        #     # If no augmentations but we need padding for consistency
        #     sequence = self._pad_end(sequence)
            
        if target is not None:
            return sequence, target
        else:
            return sequence
    
    def _get_insert_max(self) -> int:
        """Get the maximum insertion length from augmentations.
        
        Returns
        -------
        int
            Maximum insertion length found in augment_list, or 0 if none found.
            
        Notes
        -----
        This method scans through all augmentations to find the maximum
        insertion length, which is used for consistent padding when needed.
        """
        insert_max = 0
        for augment in self.augment_list:
            if hasattr(augment, 'insert_max'):
                insert_max = augment.insert_max
        return insert_max
    
    def _sample_aug_combos(self) -> List[List[int]]:
        """Sample augmentation combinations for a single sequence.
        
        Returns
        -------
        List[List[int]]
            List containing a single list of augmentation indices to apply.
            
        Notes
        -----
        - If hard_aug is True, exactly max_augs_per_seq augmentations are selected
        - If hard_aug is False, 1 to max_augs_per_seq augmentations are randomly selected
        - Augmentations are selected without replacement from the available list
        """
        if self.hard_aug:
            num_augs = self.max_augs_per_seq
        else:
            num_augs = np.random.randint(1, self.max_augs_per_seq + 1)
            
        if num_augs == 0:
            return []
            
        # Randomly choose augmentations
        aug_indices = list(sorted(np.random.choice(self.max_num_aug, num_augs, replace=False)))
        return [aug_indices]
    
    def _apply_augmentations(self, sequence: torch.Tensor) -> torch.Tensor:
        """Apply augmentations to a single sequence.
        
        Parameters
        ----------
        sequence : torch.Tensor
            Input sequence with shape (A, L) where A is number of nucleotides
            and L is sequence length.
            
        Returns
        -------
        torch.Tensor
            Augmented sequence with shape (A, L).
            
        Notes
        -----
        - The sequence is temporarily converted to batch format (1, A, L) for processing
        - Augmentations are applied sequentially in the sampled order
        - The final sequence maintains the original length L
        """
        if not self.augment_list:
            return sequence
            
        # Sample augmentation combination
        aug_combos = self._sample_aug_combos()
        if not aug_combos:
            return sequence
            
        aug_indices = aug_combos[0]
        sequence = sequence.unsqueeze(0)  # Add batch dimension
        
        # Apply augmentations
        insert_status = True
        for aug_index in aug_indices:
            sequence = self.augment_list[aug_index](sequence)
            if hasattr(self.augment_list[aug_index], 'insert_max'):
                insert_status = False
                
        # # Add padding only if no insertion augmentations were applied AND augmentations are enabled
        # if insert_status and self.insert_max > 0 and self.apply_augmentations:
        #     sequence = self._pad_end(sequence)
            
        return sequence.squeeze(0)  # Remove batch dimension
    
    def _pad_end(self, sequence: torch.Tensor) -> torch.Tensor:
        """Add random DNA padding to the end of a sequence.
        
        Parameters
        ----------
        sequence : torch.Tensor
            Input sequence with shape (A, L) or (N, A, L).
            
        Returns
        -------
        torch.Tensor
            Sequence with random DNA padding added to the end.
            
        Notes
        -----
        - Padding length is determined by self.insert_max
        - Random DNA is generated using uniform nucleotide distribution
        - This method handles both single sequences and batches
        """
        if self.insert_max <= 0:
            return sequence
            
        # Handle both single sequences and batches
        if sequence.dim() == 3:  # Batch of sequences
            N, A, L = sequence.shape
            a = torch.eye(A)
            p = torch.tensor([1/A for _ in range(A)])
            padding = torch.stack([a[p.multinomial(self.insert_max, replacement=True)].transpose(0,1) 
                                 for _ in range(N)]).to(sequence.device)
            return torch.cat([sequence, padding], dim=2)
        else:  # Single sequence
            A, L = sequence.shape
            a = torch.eye(A)
            p = torch.tensor([1/A for _ in range(A)])
            padding = a[p.multinomial(self.insert_max, replacement=True)].transpose(0,1).to(sequence.device)
            return torch.cat([sequence, padding], dim=1)
    
    def enable_augmentations(self):
        """Enable augmentations for training.
        
        Notes
        -----
        This method allows augmentations to be applied during training
        while keeping them disabled for validation/finetuning.
        """
        self.apply_augmentations = True
    
    def disable_augmentations(self):
        """Disable augmentations for finetuning/validation.
        
        Notes
        -----
        This method prevents augmentations from being applied, useful
        for validation, testing, or finetuning on original data.
        """
        self.apply_augmentations = False


class RobustLoader(DataLoader):
    """
    EvoAug2 DataLoader that inherits from PyTorch DataLoader.
    
    This class provides a DataLoader with built-in EvoAug augmentations that can be
    used with pl.DataModule or directly into vanilla PyTorch.
    
    Parameters
    ----------
    base_dataset : torch.utils.data.Dataset
        The underlying dataset that provides (sequence, target) pairs.
    augment_list : List[AugmentBase], optional
        List of augmentations to apply. Defaults to empty list.
    max_augs_per_seq : int, optional
        Maximum augmentations per sequence. Defaults to 0.
    hard_aug : bool, optional
        Whether to use hard augmentation count. Defaults to True.
    batch_size : int, optional
        Batch size for the DataLoader. Defaults to 32.
    shuffle : bool, optional
        Whether to shuffle the data. Defaults to True.
    num_workers : int, optional
        Number of worker processes. Defaults to 4.
    **kwargs
        Additional arguments passed to DataLoader.
        
    Notes
    -----
    - The RobustLoader automatically creates an AugmentedGenomicDataset wrapper
    - Augmentations can be enabled/disabled at runtime using enable_augmentations()
      and disable_augmentations() methods
    - All augmentations preserve sequence length L for consistent batch shapes
    """
    
    def __init__(self,
                 base_dataset: Dataset,
                 augment_list: List[AugmentBase] = [],
                 max_augs_per_seq: int = 0,
                 hard_aug: bool = True,
                 batch_size: int = 32,
                 shuffle: bool = True,
                 num_workers: int = 4,
                 **kwargs):
        
        # Create the augmented dataset
        self.augmented_dataset = AugmentedGenomicDataset(
            base_dataset=base_dataset,
            augment_list=augment_list,
            max_augs_per_seq=max_augs_per_seq,
            hard_aug=hard_aug,
            apply_augmentations=True
        )
        
        # Initialize the parent DataLoader with the augmented dataset
        super().__init__(
            dataset=self.augmented_dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            **kwargs
        )
    
    def enable_augmentations(self):
        """Enable augmentations for training.
        
        Notes
        -----
        This method enables augmentations on the underlying dataset,
        allowing them to be applied during training.
        """
        self.augmented_dataset.enable_augmentations()
    
    def disable_augmentations(self):
        """Disable augmentations for finetuning/validation.
        
        Notes
        -----
        This method disables augmentations on the underlying dataset,
        useful for validation, testing, or finetuning on original data.
        """
        self.augmented_dataset.disable_augmentations()
    
    def set_augmentations(self, augment_list: List[AugmentBase], max_augs_per_seq: int = 0, hard_aug: bool = True):
        """Update the augmentation settings.
        
        Parameters
        ----------
        augment_list : List[AugmentBase]
            New list of augmentations to apply.
        max_augs_per_seq : int, optional
            New maximum augmentations per sequence. Defaults to 0.
        hard_aug : bool, optional
            New hard augmentation setting. Defaults to True.
            
        Notes
        -----
        This method allows dynamic updating of augmentation parameters
        without recreating the entire DataLoader.
        """
        self.augmented_dataset.augment_list = augment_list
        self.augmented_dataset.max_augs_per_seq = min(max_augs_per_seq, len(augment_list))
        self.augmented_dataset.hard_aug = hard_aug
        self.augmented_dataset.max_num_aug = len(augment_list)
        self.augmented_dataset.insert_max = self.augmented_dataset._get_insert_max()
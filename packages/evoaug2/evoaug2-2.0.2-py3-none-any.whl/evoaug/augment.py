"""
Library of data augmentations for genomic sequence data.

This module provides evolution-inspired data augmentation techniques for genomic sequences,
ensuring that all augmentations preserve the input sequence length L.

To contribute a custom augmentation, use the following syntax:

.. code-block:: python

    class CustomAugmentation(AugmentBase):
        def __init__(self, param1, param2):
            self.param1 = param1
            self.param2 = param2

        def __call__(self, x: torch.Tensor) -> torch.Tensor:
            # Perform augmentation
            return x_aug

"""

import torch


class AugmentBase:
    """
    Base class for EvoAug augmentations for genomic sequences.
    
    All augmentation classes should inherit from this base class and implement
    the :meth:`__call__` method to ensure consistent interface.
    """
    
    def __call__(self, x):
        """Return an augmented version of `x`.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L) where:
            - N is the batch size
            - A is the number of nucleotides (4 for DNA)
            - L is the sequence length

        Returns
        -------
        torch.Tensor
            Batch of one-hot sequences with random augmentation applied.
            Output shape must be (N, A, L) to maintain sequence length consistency.

        Raises
        ------
        NotImplementedError
            If the augmentation class does not implement this method.
        """
        raise NotImplementedError()


class RandomDeletion(AugmentBase):
    """
    Randomly deletes contiguous stretches of nucleotides from sequences.
    
    This augmentation randomly selects deletion lengths and positions for each sequence
    in a batch, then pads the deleted regions with random DNA to maintain the original
    sequence length L.

    Parameters
    ----------
    delete_min : int, optional
        Minimum size for random deletion. Defaults to 0.
    delete_max : int, optional
        Maximum size for random deletion. Defaults to 20.
        
    Notes
    -----
    - Deletion positions are constrained to ensure the deletion window fits within
      the sequence boundaries
    - Random DNA padding is added equally to both ends of the deletion to maintain
      sequence length L
    - Each sequence in the batch receives a different random deletion
    """
    
    def __init__(self, delete_min=0, delete_max=20):
        self.delete_min = delete_min
        self.delete_max = delete_max

    def __call__(self, x):
        """Randomly delete segments in a set of one-hot DNA sequences.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with randomly deleted segments, padded with random DNA
            to maintain shape (N, A, L).
        """
        N, A, L = x.shape

        # sample random DNA
        a = torch.eye(A)
        p = torch.tensor([1/A for _ in range(A)])
        padding = torch.stack([a[p.multinomial(self.delete_max, replacement=True)].transpose(0,1) for _ in range(N)]).to(x.device)

        # sample deletion length for each sequence
        delete_lens = torch.randint(self.delete_min, self.delete_max + 1, (N,))

        # sample locations to delete for each sequence
        delete_inds = torch.randint(L - self.delete_max + 1, (N,)) # deletion must be in boundaries of seq.

        # loop over each sequence
        x_aug = []
        for seq, pad, delete_len, delete_ind in zip(x, padding, delete_lens, delete_inds):

            # get index of half delete_len (to pad random DNA at beginning of sequence)
            pad_begin_index = torch.div(delete_len, 2, rounding_mode='floor').item()

            # index for other half (to pad random DNA at end of sequence)
            pad_end_index = delete_len - pad_begin_index

            # removes deletion and pads beginning and end of sequence with random DNA to ensure same length
            x_aug.append( torch.cat([pad[:,:pad_begin_index],                # random dna padding
                                     seq[:,:delete_ind],                     # sequence up to deletion start index
                                     seq[:,delete_ind+delete_len:],          # sequence after deletion end index
                                     pad[:,self.delete_max-pad_end_index:]], # random dna padding
                                    -1)) # concatenation axis
        return torch.stack(x_aug)


class RandomInsertion(AugmentBase):
    """
    Randomly inserts contiguous stretches of random DNA into sequences.
    
    This augmentation randomly selects insertion lengths and positions for each sequence
    in a batch, then trims the resulting sequences equally from both ends to maintain
    the original sequence length L.

    Parameters
    ----------
    insert_min : int, optional
        Minimum size for random insertion. Defaults to 0.
    insert_max : int, optional
        Maximum size for random insertion. Defaults to 20.
        
    Notes
    -----
    - Insertion positions are randomly selected across the sequence length
    - Random DNA is generated using uniform nucleotide distribution
    - After insertion, sequences are trimmed equally from both ends to maintain
      sequence length L
    - Each sequence in the batch receives a different random insertion
    """
    
    def __init__(self, insert_min=0, insert_max=20):
        self.insert_min = insert_min
        self.insert_max = insert_max
    
    def __call__(self, x):
        """Randomly insert segments of random DNA into DNA sequences.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with randomly inserted segments of random DNA, trimmed
            to maintain shape (N, A, L).
        """
        N, A, L = x.shape
        # If insert_max is 0, return original sequences without modification
        if self.insert_max <= 0:
            return x

        # sample random DNA
        a = torch.eye(A)
        p = torch.tensor([1/A for _ in range(A)])
        insertions = torch.stack([a[p.multinomial(self.insert_max, replacement=True)].transpose(0,1) for _ in range(N)]).to(x.device)

        # sample insertion length for each sequence
        insert_lens = torch.randint(self.insert_min, self.insert_max + 1, (N,))

        # sample locations to insertion for each sequence
        insert_inds = torch.randint(L, (N,))

        # loop over each sequence
        x_aug = []
        for seq, insertion, insert_len, insert_ind in zip(x, insertions, insert_lens, insert_inds):
            # Convert to Python integers for safe indexing
            il = insert_len.item()
            ii = insert_ind.item()
            
            # Insert the random DNA
            inserted = torch.cat([seq[:, :ii], insertion[:, :il], seq[:, ii:]], -1)
            
            # Calculate how much to trim to get back to length L
            current_len = inserted.shape[-1]
            excess = current_len - L
            
            if excess > 0:
                # Trim equally from both ends
                trim_left = excess // 2
                trim_right = excess - trim_left
                final_seq = inserted[:, trim_left:current_len - trim_right]
            else:
                # No trimming needed
                final_seq = inserted
            
            # Ensure the final sequence has exactly length L
            if final_seq.shape[-1] != L:
                # If still wrong length, pad or trim to exactly L
                if final_seq.shape[-1] > L:
                    final_seq = final_seq[:, :L]
                else:
                    # Pad with random DNA to reach length L
                    padding_needed = L - final_seq.shape[-1]
                    padding = a[p.multinomial(padding_needed, replacement=True)].transpose(0,1).to(x.device)
                    final_seq = torch.cat([final_seq, padding], -1)
            
            x_aug.append(final_seq)

        # Stack all sequences and ensure they all have the same shape
        stacked = torch.stack(x_aug)
        
        # Final safety check - ensure all sequences have exactly length L
        if stacked.shape[-1] != L:
            print(f"Warning: RandomInsertion output shape {stacked.shape} doesn't match expected length {L}")
            # Force all sequences to length L by trimming or padding
            if stacked.shape[-1] > L:
                stacked = stacked[:, :, :L]
            else:
                # Pad all sequences to length L
                padding_needed = L - stacked.shape[-1]
                padding = torch.stack([a[p.multinomial(padding_needed, replacement=True)].transpose(0,1) for _ in range(N)]).to(x.device)
                stacked = torch.cat([stacked, padding], -1)
        
        return stacked


class RandomTranslocation(AugmentBase):
    """
    Randomly shifts sequences using circular roll transformations.
    
    This augmentation applies random positive or negative shifts to each sequence
    in a batch, effectively cutting the sequence and reordering the pieces
    while maintaining the original sequence length L.

    Parameters
    ----------
    shift_min : int, optional
        Minimum size for random shift. Defaults to 0.
    shift_max : int, optional
        Maximum size for random shift. Defaults to 20.
        
    Notes
    -----
    - Shifts are randomly chosen between shift_min and shift_max
    - Approximately half of the shifts are made negative to create
      both left and right circular shifts
    - Uses torch.roll for efficient implementation
    - Each sequence in the batch receives a different random shift
    """
    
    def __init__(self, shift_min=0, shift_max=20):
        self.shift_min = shift_min
        self.shift_max = shift_max

    def __call__(self, x):
        """Randomly shift sequences in a batch using circular roll.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with random circular shifts applied, maintaining
            shape (N, A, L).
        """
        N = x.shape[0]

        # determine size of shifts for each sequence
        shifts = torch.randint(self.shift_min, self.shift_max + 1, (N,))

        # make some of the shifts negative
        ind_neg = torch.rand(N) < 0.5
        shifts[ind_neg] = -1 * shifts[ind_neg]

        # apply random shift to each sequence
        x_rolled = []
        for i, shift in enumerate(shifts):
            x_rolled.append( torch.roll(x[i], shift.item(), -1) )
        x_rolled = torch.stack(x_rolled).to(x.device)
        return x_rolled


class RandomInversion(AugmentBase):
    """
    Randomly inverts contiguous stretches of nucleotides in sequences.
    
    This augmentation randomly selects inversion lengths and positions for each sequence
    in a batch, then applies a reverse-complement transformation to the selected region
    while maintaining the original sequence length L.

    Parameters
    ----------
    invert_min : int, optional
        Minimum size for random inversion. Defaults to 0.
    invert_max : int, optional
        Maximum size for random inversion. Defaults to 20.
        
    Notes
    -----
    - Inversion positions are constrained to ensure the inversion window fits within
      the sequence boundaries
    - Applies reverse-complement transformation (flip both sequence and nucleotide dimensions)
    - Each sequence in the batch receives a different random inversion
    """
    
    def __init__(self, invert_min=0, invert_max=20):
        self.invert_min = invert_min
        self.invert_max = invert_max

    def __call__(self, x):
        """Randomly invert segments of DNA sequences.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with randomly inverted segments, maintaining
            shape (N, A, L).
        """
        N, A, L = x.shape

        # set random inversion size for each sequence
        inversion_lens = torch.randint(self.invert_min, self.invert_max + 1, (N,))

        # randomly select start location for each inversion
        inversion_inds = torch.randint(L - self.invert_max + 1, (N,)) # inversion must be in boundaries of seq.

        # apply random inversion to each sequence
        x_aug = []
        for seq, inversion_len, inversion_ind in zip(x, inversion_lens, inversion_inds):
            x_aug.append( torch.cat([seq[:,:inversion_ind],    # sequence up to inversion start index
                                     torch.flip(seq[:,inversion_ind:inversion_ind+inversion_len], dims=[0,1]), # reverse-complement transformation
                                     seq[:,inversion_ind+inversion_len:]], # sequence after inversion
                                    -1)) # concatenation axis
        return torch.stack(x_aug)


class RandomMutation(AugmentBase):
    """
    Randomly mutates nucleotides in sequences according to a mutation fraction.
    
    This augmentation randomly selects positions in each sequence and replaces
    the nucleotides with random DNA, effectively introducing point mutations
    while maintaining the original sequence length L.

    Parameters
    ----------
    mutate_frac : float, optional
        Probability of mutation for each nucleotide. Defaults to 0.05.
        
    Notes
    -----
    - The actual number of mutations is calculated as: round(mutate_frac / 0.75 * L)
    - The division by 0.75 accounts for silent mutations (nucleotides that don't change)
    - Random DNA is generated using uniform nucleotide distribution
    - Each sequence in the batch receives a different set of random mutations
    """
    
    def __init__(self, mut_frac=0.05):
        self.mutate_frac = mut_frac

    def __call__(self, x):
        """Randomly introduce mutations to a set of one-hot DNA sequences.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with randomly mutated DNA, maintaining
            shape (N, A, L).
        """
        N, A, L = x.shape

        # determine the number of mutations per sequence
        num_mutations = round(self.mutate_frac / 0.75 * L) # num. mutations per sequence (accounting for silent mutations)

        # If no mutations, return original sequences
        if num_mutations <= 0:
            return x

        # randomly determine the indices to apply mutations
        mutation_inds = torch.argsort(torch.rand(N,L))[:, :num_mutations] # see <https://discuss.pytorch.org/t/torch-equivalent-of-numpy-random-choice/16146>0

        # create random DNA (to serve as random mutations)
        a = torch.eye(A)
        p = torch.tensor([1/A for _ in range(A)])
        mutations = torch.stack([a[p.multinomial(num_mutations, replacement=True)].transpose(0,1) for _ in range(N)]).to(x.device)

        # make a copy of the batch of sequences
        x_aug = torch.clone(x)

        # loop over sequences and apply mutations
        for i in range(N):
            x_aug[i,:,mutation_inds[i]] = mutations[i]
        return x_aug


class RandomRC(AugmentBase):
    """
    Randomly applies reverse-complement transformations to sequences.
    
    This augmentation randomly selects sequences in a batch and applies
    a reverse-complement transformation with a specified probability.
    The transformation reverses both the sequence order and nucleotide
    identity while maintaining the original sequence length L.

    Parameters
    ----------
    rc_prob : float, optional
        Probability to apply a reverse-complement transformation. Defaults to 0.5.
        
    Notes
    -----
    - Each sequence is independently selected for transformation
    - Uses torch.flip with dims=[1,2] to reverse both sequence and nucleotide dimensions
    - Maintains original sequence length L
    - Useful for learning strand-invariant representations
    """
    
    def __init__(self, rc_prob=0.5):
        """Create random reverse-complement augmentation object.
        
        Parameters
        ----------
        rc_prob : float
            Probability to apply reverse-complement transformation.
        """
        self.rc_prob = rc_prob

    def __call__(self, x):
        """Randomly transform sequences with reverse-complement transformations.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with random reverse-complements applied, maintaining
            shape (N, A, L).
        """
        # make a copy of the sequence
        x_aug = torch.clone(x)

        # randomly select sequences to apply rc transformation
        ind_rc = torch.rand(x_aug.shape[0]) < self.rc_prob

        # apply reverse-complement transformation
        x_aug[ind_rc] = torch.flip(x_aug[ind_rc], dims=[1,2])
        return x_aug


class RandomNoise(AugmentBase):
    """
    Randomly adds Gaussian noise to sequences.
    
    This augmentation adds random Gaussian noise to each sequence in a batch,
    effectively introducing small perturbations to the one-hot encodings
    while maintaining the original sequence length L.

    Parameters
    ----------
    noise_mean : float, optional
        Mean of the Gaussian noise. Defaults to 0.0.
    noise_std : float, optional
        Standard deviation of the Gaussian noise. Defaults to 0.2.
        
    Notes
    -----
    - Noise is sampled from a normal distribution with specified mean and standard deviation
    - Noise is added element-wise to the input tensor
    - Useful for improving model robustness to small perturbations
    - Each sequence in the batch receives different random noise
    """
    
    def __init__(self, noise_mean=0.0, noise_std=0.2):
        self.noise_mean = noise_mean
        self.noise_std = noise_std

    def __call__(self, x):
        """Randomly add Gaussian noise to a set of one-hot DNA sequences.

        Parameters
        ----------
        x : torch.Tensor
            Batch of one-hot sequences with shape (N, A, L).

        Returns
        -------
        torch.Tensor
            Sequences with random noise added, maintaining
            shape (N, A, L).
        """
        return x + torch.normal(self.noise_mean, self.noise_std, x.shape).to(x.device)
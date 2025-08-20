# EvoAug2

EvoAug2 is a PyTorch package to pretrain sequence-based deep learning models for regulatory genomics with evolution-inspired data augmentations, followed by fine-tuning on the original, unperturbed data. The new version replaces the prior model-wrapper (`RobustModel`) with a loader-first design (`RobustLoader`) that applies augmentations on-the-fly within a drop-in `DataLoader`.

All augmentations are length-preserving: inputs with shape (N, A, L) always return outputs with the exact same shape.

For questions, email: koo@cshl.edu

<img src="fig/augmentations.png" alt="fig" width="500"/>

<img src="fig/overview.png" alt="overview" width="500"/>


## Install

```bash
pip install evoaug2
```


## Dependencies

```text
torch >= 1.9.0
pytorch-lightning >= 1.5.0
numpy >= 1.20.0
scipy >= 1.7.0
h5py >= 3.1.0
```

Note: The examples use `pytorch_lightning` (imported as `import pytorch_lightning as pl`). If you use the newer `lightning.pytorch` package, adapt the `Trainer` import and arguments accordingly.


## What changed (RobustModel → RobustLoader)

- The training wrapper is no longer required. Instead of wrapping a model in `RobustModel`, EvoAug2 provides a `RobustLoader` that augments data during loading.
- Works with any PyTorch model, any dataset returning `(sequence, target)` with `sequence` shaped as (A, L).
- Augmentations can be toggled per-loader: `loader.enable_augmentations()` / `loader.disable_augmentations()`.
- Fine-tuning stage is implemented by disabling augmentations on the same dataset/loader.

Quick migration:
- Before: wrap model with `evoaug.RobustModel(...)` and pass a normal DataLoader.
- Now: create a `RobustLoader(base_dataset, augment_list, ...)` and pass the loader to your Trainer or training loop.


## Augmentations

```python
from evoaug import augment

augment_list = [
    augment.RandomDeletion(delete_min=0, delete_max=30),
    augment.RandomTranslocation(shift_min=0, shift_max=20),
    augment.RandomInsertion(insert_min=0, insert_max=20),
    augment.RandomRC(rc_prob=0.0),
    augment.RandomMutation(mut_frac=0.05),
    augment.RandomNoise(noise_mean=0.0, noise_std=0.3),
]
```
All transforms keep sequence length exactly L and operate on batches shaped (N, A, L).


## Use case 1: Lightning DataModule over a base dataset

This pattern mirrors `example_training.py` and is recommended for the two-stage workflow.

```python
import pytorch_lightning as pl
from evoaug.evoaug import RobustLoader
from evoaug import augment
from utils import utils  # provides H5Dataset with train/val/test splits

# Define augmentations (DeepSTARR-optimal shown in example_training.py)
augment_list = [
    # augment.RandomDeletion(delete_min=0, delete_max=30),
    augment.RandomTranslocation(shift_min=0, shift_max=20),
    # augment.RandomInsertion(insert_min=0, insert_max=20),
    augment.RandomRC(rc_prob=0.0),
    augment.RandomMutation(mut_frac=0.05),
    augment.RandomNoise(noise_mean=0.0, noise_std=0.3),
]

# Base dataset (returns per-split datasets)
base = utils.H5Dataset(filepath, batch_size=batch_size, lower_case=False, transpose=False)

class AugmentedDataModule(pl.LightningDataModule):
    def __init__(self, base_dataset, augment_list, max_augs_per_seq, hard_aug):
        super().__init__()
        self.base_dataset = base_dataset
        self.augment_list = augment_list
        self.max_augs_per_seq = max_augs_per_seq
        self.hard_aug = hard_aug

    def train_dataloader(self):
        train_ds = self.base_dataset.get_train_dataset()
        return RobustLoader(
            base_dataset=train_ds,
            augment_list=self.augment_list,
            max_augs_per_seq=self.max_augs_per_seq,
            hard_aug=self.hard_aug,
            batch_size=self.base_dataset.batch_size,
            shuffle=True,
        )

    def val_dataloader(self):
        val_ds = self.base_dataset.get_val_dataset()
        loader = RobustLoader(
            base_dataset=val_ds,
            augment_list=self.augment_list,
            max_augs_per_seq=self.max_augs_per_seq,
            hard_aug=self.hard_aug,
            batch_size=self.base_dataset.batch_size,
            shuffle=False,
        )
        loader.disable_augmentations()  # no augs for validation
        return loader

    def test_dataloader(self):
        test_ds = self.base_dataset.get_test_dataset()
        loader = RobustLoader(
            base_dataset=test_ds,
            augment_list=self.augment_list,
            max_augs_per_seq=self.max_augs_per_seq,
            hard_aug=self.hard_aug,
            batch_size=self.base_dataset.batch_size,
            shuffle=False,
        )
        loader.disable_augmentations()  # no augs for test
        return loader

# Stage 1: pretrain with augmentations (e.g., 100 epochs)
data_module = AugmentedDataModule(base, augment_list, max_augs_per_seq=2, hard_aug=True)
trainer = pl.Trainer(max_epochs=100, accelerator='auto', devices='auto')
trainer.fit(model, datamodule=data_module)

# Stage 2: fine-tune on original data (disable augmentations)
class FineTuneDataModule(pl.LightningDataModule):
    def __init__(self, base_dataset):
        super().__init__()
        self.base_dataset = base_dataset
    def train_dataloader(self):
        return self.base_dataset.train_dataloader()
    def val_dataloader(self):
        return self.base_dataset.val_dataloader()
    def test_dataloader(self):
        return self.base_dataset.test_dataloader()

finetune_dm = FineTuneDataModule(base)
trainer_finetune = pl.Trainer(max_epochs=5, accelerator='auto', devices='auto')
trainer_finetune.fit(model_finetune, datamodule=finetune_dm)
```


## Use case 2: Vanilla PyTorch loop with RobustLoader

```python
from evoaug.evoaug import RobustLoader
from evoaug import augment

# Your dataset must return (sequence, target) with sequence shape (A, L)
base_dataset = YourDataset(...)
augment_list = [
    augment.RandomTranslocation(shift_min=0, shift_max=20),
    augment.RandomRC(rc_prob=0.0),
    augment.RandomMutation(mut_frac=0.05),
    augment.RandomNoise(noise_mean=0.0, noise_std=0.3),
]

train_loader = RobustLoader(
    base_dataset=base_dataset,
    augment_list=augment_list,
    max_augs_per_seq=2,
    hard_aug=True,
    batch_size=128,
    shuffle=True,
    num_workers=4,
)

for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:  # x is (N, A, L)
        x = x.to(device)
        y = y.to(device)
        optimizer.zero_grad()
        y_hat = model(x)
        loss = criterion(y_hat, y)
        loss.backward()
        optimizer.step()

# Validation/test: either use your original non-augmented loader
# or temporarily disable augmentations on the same loader
# train_loader.disable_augmentations()
# for x, y in val_loader: ...
```


## Optional: checkpointing and plotting

EvoAug2 leaves checkpointing/plotting to user code. They are easy to add, and `example_training.py` shows complete, ready-to-use helpers.

- Checkpoints (best-practice): use `pytorch_lightning` callbacks

```python
import os
import pytorch_lightning as pl

ckpt_name = f"{expt_name}_aug"
ckpt_cb = pl.callbacks.ModelCheckpoint(
    monitor='val_loss', save_top_k=1,
    dirpath=output_dir, filename=ckpt_name,
)
trainer = pl.Trainer(callbacks=[ckpt_cb], max_epochs=100, accelerator='auto', devices='auto')
# trainer.fit(...)

best_ckpt_path = os.path.join(output_dir, ckpt_name + '.ckpt')
# model = LightningModule.load_from_checkpoint(best_ckpt_path, model=model_arch)
```

- Skipping redundant runs: a minimal helper

```python
import os, torch

def check_existing_checkpoints(output_dir, expt_name):
    paths = {
        'augmented': os.path.join(output_dir, f"{expt_name}_aug.ckpt"),
        'finetuned': os.path.join(output_dir, f"{expt_name}_finetune.ckpt"),
        'control':   os.path.join(output_dir, f"{expt_name}_standard.ckpt"),
    }
    return {k: (os.path.exists(p), p) for k, p in paths.items()}
```

- Plotting performance: compute metrics (Pearson/Spearman) from predictions and create comparison plots with matplotlib/seaborn. See `example_training.py` for a comprehensive `plot_metrics_comparison(...)` implementation.


## API overview

- `AugmentedGenomicDataset(base_dataset, augment_list, max_augs_per_seq=0, hard_aug=True, apply_augmentations=True)`
  - Wraps any dataset and applies augmentations on-the-fly.
  - `enable_augmentations()` / `disable_augmentations()` to toggle.
- `RobustLoader(base_dataset, augment_list, max_augs_per_seq, hard_aug, batch_size, shuffle, num_workers, ...)`
  - Inherits from `torch.utils.data.DataLoader`.
  - `enable_augmentations()` / `disable_augmentations()` on the underlying dataset.
  - `set_augmentations(augment_list, max_augs_per_seq, hard_aug)` to update settings without recreating the loader.

All augmentations preserve sequence length L for stable model shapes across training/validation.


## Two-stage workflow (recommended)

1. Pretrain with EvoAug2 augmentations using `RobustLoader` (e.g., 100 epochs).
2. Fine-tune the same architecture on original data with augmentations disabled (e.g., 5 epochs, lower LR).
3. Optionally, train a control model on original data only for baseline comparison.

This mirrors the EvoAug methodology and typically improves robustness and generalization.


## Reference

- Paper: "EvoAug: improving generalization and interpretability of genomic deep neural networks with evolution-inspired data augmentations" (Genome Biology, 2023).

```bibtex
@article{lee2023evoaug,
  title={EvoAug: improving generalization and interpretability of genomic deep neural networks with evolution-inspired data augmentations},
  author={Lee, Nicholas Keone and Tang, Ziqi and Toneyan, Shushan and Koo, Peter K},
  journal={Genome Biology},
  volume={24},
  number={1},
  pages={105},
  year={2023},
  publisher={Springer}
}
``` 
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

## Installation Options

### **Option 1: Install from PyPI (Recommended)**

```bash
# Install the latest stable release
pip install evoaug2

# Install with specific version
pip install evoaug2==2.0.2

# Install with optional dependencies for examples
pip install evoaug2[examples]

# Install with all optional dependencies
pip install evoaug2[full]
```

### **Option 2: Install from Source (Development)**

```bash
# Clone the repository
git clone https://github.com/aduranu/evoaug.git
cd evoaug2

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### **Option 3: Install with Conda/Mamba**

```bash
# Create a new environment (recommended)
conda create -n evoaug2 python=3.8
conda activate evoaug2

# Install PyTorch first (choose appropriate version)
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia

# Install EvoAug2
pip install evoaug2
```

## Dependencies

```text
torch >= 1.9.0
pytorch-lightning >= 1.5.0
numpy >= 1.20.0
scipy >= 1.7.0
h5py >= 3.1.0
scikit-learn >= 1.0.0
```

Note: The examples use `pytorch_lightning` (imported as `import pytorch_lightning as pl`). If you use the newer `lightning.pytorch` package, adapt the `Trainer` import and arguments accordingly.

## Quick Start

```python
# Install the package
pip install evoaug2

# Import and use
from evoaug import evoaug, augment
from utils import utils

# Create augmentations
augment_list = [
    augment.RandomDeletion(delete_min=0, delete_max=20),
    augment.RandomRC(rc_prob=0.5),
    augment.RandomMutation(mut_frac=0.05),
]

# Create a RobustLoader
loader = evoaug.RobustLoader(
    base_dataset=your_dataset,
    augment_list=augment_list,
    max_augs_per_seq=2,
    hard_aug=True,
    batch_size=32
)

# Use in training
for x, y in loader:
    # x has shape (N, A, L) with augmentations applied
    # Your training code here
    pass
```

## Use Cases

EvoAug2 provides two main usage patterns, both demonstrated in the included example scripts:

### **Use Case 1: PyTorch Lightning DataModule (Recommended)**

The `example_lightning_module.py` script demonstrates the complete two-stage training workflow:

```python
from evoaug.evoaug import RobustLoader
from evoaug import augment
import pytorch_lightning as pl

# Define augmentations
augment_list = [
    augment.RandomTranslocation(shift_min=0, shift_max=20),
    augment.RandomRC(rc_prob=0.0),
    augment.RandomMutation(mut_frac=0.05),
    augment.RandomNoise(noise_mean=0.0, noise_std=0.3),
]

# Create Lightning DataModule with augmentations
class AugmentedDataModule(pl.LightningDataModule):
    def __init__(self, base_dataset, augment_list, max_augs_per_seq, hard_aug):
        super().__init__()
        self.base_dataset = base_dataset
        self.augment_list = augment_list
        self.max_augs_per_seq = max_augs_per_seq
        self.hard_aug = hard_aug
        
    def train_dataloader(self):
        # Training with augmentations
        train_dataset = self.base_dataset.get_train_dataset()
        return RobustLoader(
            base_dataset=train_dataset,
            augment_list=self.augment_list,
            max_augs_per_seq=self.max_augs_per_seq,
            hard_aug=self.hard_aug,
            batch_size=self.base_dataset.batch_size,
            shuffle=True
        )
    
    def val_dataloader(self):
        # Validation without augmentations
        val_dataset = self.base_dataset.get_val_dataset()
        loader = RobustLoader(
            base_dataset=val_dataset,
            augment_list=self.augment_list,
            max_augs_per_seq=self.max_augs_per_seq,
            hard_aug=self.hard_aug,
            batch_size=self.base_dataset.batch_size,
            shuffle=False
        )
        loader.disable_augmentations()  # No augs for validation
        return loader

# Two-stage training workflow
# Stage 1: Train with augmentations
data_module = AugmentedDataModule(base_dataset, augment_list, max_augs_per_seq=2, hard_aug=True)
trainer = pl.Trainer(max_epochs=100, accelerator='auto', devices='auto')
trainer.fit(model, datamodule=data_module)

# Stage 2: Fine-tune on original data
class FineTuneDataModule(pl.LightningDataModule):
    def __init__(self, base_dataset):
        super().__init__()
        self.base_dataset = base_dataset
    def train_dataloader(self):
        return self.base_dataset.train_dataloader()
    def val_dataloader(self):
        return self.base_dataset.val_dataloader()

finetune_dm = FineTuneDataModule(base_dataset)
trainer_finetune = pl.Trainer(max_epochs=5, accelerator='auto', devices='auto')
trainer_finetune.fit(model_finetune, datamodule=finetune_dm)
```

**Key Features:**
- Automatic checkpoint management and resuming
- Comprehensive performance comparison plots
- Two-stage training: augmentations → fine-tuning
- Control model training for baseline comparison

### **Use Case 2: Vanilla PyTorch Training Loop**

The `example_vanilla_pytorch.py` script shows direct usage without Lightning:

```python
from evoaug.evoaug import RobustLoader
from evoaug import augment
import torch
import torch.nn as nn

# Create augmentations
augment_list = [
    augment.RandomTranslocation(shift_min=0, shift_max=20),
    augment.RandomRC(rc_prob=0.0),
    augment.RandomMutation(mut_frac=0.05),
    augment.RandomNoise(noise_mean=0.0, noise_std=0.3),
]

# Create RobustLoader
train_loader = RobustLoader(
    base_dataset=base_dataset,
    augment_list=augment_list,
    max_augs_per_seq=2,
    hard_aug=True,
    batch_size=128,
    shuffle=True,
    num_workers=4,
)

# Training loop
model = Model(...)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        y_hat = model(x)
        loss = criterion(y_hat, y)
        loss.backward()
        optimizer.step()
```

**Key Features:**
- Minimal dependencies (no Lightning required)
- Simple CNN architecture with global average pooling
- Direct control over training loop
- Easy to modify and extend

## Troubleshooting

### **Common Issues**

**Import Error: No module named 'evoaug'**
```bash
# Make sure you installed the correct package name
pip install evoaug2  # NOT evoaug
```

**CUDA/GPU Issues**
```bash
# Install PyTorch with CUDA support first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Then install EvoAug2
pip install evoaug2
```

**Version Conflicts**
```bash
# Create a clean environment
conda create -n evoaug2 python=3.8
conda activate evoaug2
pip install evoaug2
```


)
```

### **Getting Help**

- **GitHub Issues**: Report bugs at https://github.com/aduranu/evoaug/issues
- **Email**: koo@cshl.edu
- **Documentation**: See example scripts for complete usage examples

## Package Structure

```
evoaug2/
├── evoaug/                 # Core augmentation package
│   ├── __init__.py         # Package exports
│   ├── augment.py          # Augmentation implementations
│   └── evoaug.py           # RobustLoader and dataset classes
├── utils/                   # Utility functions
│   ├── __init__.py         # Utility exports
│   ├── model_zoo.py        # Model architectures
│   └── utils.py            # H5Dataset and evaluation tools
├── example_lightning_module.py  # Complete Lightning training example
├── example_vanilla_pytorch.py   # Simple PyTorch training example
├── setup.py                 # Package configuration
├── pyproject.toml          # Modern Python packaging
├── requirements.txt         # Core dependencies
└── README.md               # This file
```

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

## Two-stage workflow (recommended)

1. **Pretrain** with EvoAug2 augmentations using `RobustLoader` (e.g., 100 epochs).
2. **Fine-tune** the same architecture on original data with augmentations disabled (e.g., 5 epochs, lower LR).
3. **Optionally**, train a control model on original data only for baseline comparison.

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
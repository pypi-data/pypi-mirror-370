"""
Setup script for EvoAug2 package.

This script configures the EvoAug2 package for distribution and installation.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Evolution-Inspired Data Augmentation for Genomic Sequences"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements.txt file for dependencies."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Package configuration
setup(
    name="evoaug2",
    version="2.0.0",
    author="Peter K. Koo",
    author_email="koo@cshl.edu",
    description="Evolution-Inspired Data Augmentation for Genomic Sequences - DataLoader Version",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pkoo/evoaug2",
    project_urls={
        "Bug Tracker": "https://github.com/pkoo/evoaug2/issues",
        "Source Code": "https://github.com/pkoo/evoaug2",
    },
    packages=find_packages(include=['evoaug', 'evoaug.*', 'utils', 'utils.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.15",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.12",
            "myst-parser>=0.15",
            "nbsphinx>=0.8",
        ],
        "examples": [
            "matplotlib>=3.3",
            "seaborn>=0.11",
            "jupyter>=1.0",
            "ipywidgets>=7.6",
        ],
        "full": [
            "torch>=1.9.0",
            "torchvision>=0.10.0",
            "pytorch-lightning>=1.5.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
            "h5py>=3.1.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
        ],
    },
    keywords=[
        "genomics",
        "data-augmentation", 
        "deep-learning",
        "pytorch",
        "bioinformatics",
        "sequence-analysis",
        "evolution",
        "mutations",
        "machine-learning",
        "neural-networks",
        "dna",
        "rna",
        "sequence",
        "motif",
        "regulatory",
        "transcription",
        "chromatin",
    ],
    include_package_data=True,
    package_data={
        "evoaug": ["*.py", "*.pyi"],
        "utils": ["*.py", "*.pyi"],
    },
    zip_safe=False,
    # Metadata for PyPI
    license="MIT",
    platforms=["any"],
    maintainer="Peter K. Koo",
    maintainer_email="koo@cshl.edu",
    
    # Additional metadata
    provides=["evoaug2"],
    requires_python=">=3.8",
    setup_requires=[
        "setuptools>=45",
        "wheel",
    ],
)

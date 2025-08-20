# Neutrophils Maturation Classifier App

![alt text](./doc/screenshot.png "Screenshot")

A minimal 3D neutrophil maturation classification app with convolution neural network.

## Overview

This application allows for the automated classification of neutrophils at different maturation stages using a 3D convolutional neural network. It's designed to assist researchers and clinicians in analyzing 3D neutrophil morphology with geometric and CNN embedded features.

**Note**: GPU runtime only available on Linux.

## Features

- 3D visualization of neutrophil isosurfaces
- Real-time classification of neutrophil maturation stages
- Support for TIFF image input
- Batch processing capabilities

## Installation
### Installation with Conda (Mamba)

1. [Download Miniforge](https://github.com/conda-forge/miniforge#miniforge3) and install it if you don't have conda/mamba.
2. Create and activate a new environment:
    ```bash
    mamba create -n neutrophils python=3.10
    mamba activate neutrophils
    ```
3. Install the package:
    ```bash
    pip install neutrophils-classifier-app
    ```

**Note**: This package now uses the published `neutrophils-core` library from PyPI, which provides the core machine learning functionality.

### Run the App
```bash
neutrophil-classifier
```

*Note*: The first launch may take up to 10 minutes as the application performs initial setup and caching. Subsequent startups will be significantly faster.

## For Developers

### Development Setup
1. Set up the conda environment:
```bash
git clone git@github.com:bpi-oxford/Neutrophils-Classifier-App.git
cd Neutrophils-Classifier-App
git submodule update --init --recursive
mamba env create -f env.yaml
mamba activate neutrophils
```

2. Install in editable mode:
```bash
pip install -e .
```

3. Run the application:
```bash
neutrophil-classifier
```

### Packaging Setup
1. Set up the conda environment:
```bash
mamba env create -f env-minimal.yaml
mamba activate neutrophils-minimal
```

2. See [`BUILD_GUIDE.md`](BUILD_GUIDE.md) for detailed build and publish instructions.
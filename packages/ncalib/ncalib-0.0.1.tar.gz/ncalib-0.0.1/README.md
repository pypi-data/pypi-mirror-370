# ncalib
A modular Python Library for handling Neural Cellular Automata.

## Features

- Modular architecture for Neural Cellular Automata
- Easy-to-use API for building and training NCA models
- Extensible framework for custom implementations


## Quickstart
### Installation

Install ncalib from PyPI using pip:

```bash
pip install ncalib
```
Some examples and loggers are using [Weights and Biases](https://wandb.ai/). To use them install the required dependencies using:
```bash
pip install ncalib[wandb]
```
### Examples
Examples are found in ``examples``. Currently there are following implementations:
- [simple_nca.py](/examples/simple_nca.py) - Original NCA reconstructing an image ([Mordvintsev et al. (2020)](https://distill.pub/2020/growing-ca/))
- [simple_classifying_mnist.py](/examples/self_classifying_mnist.py) - Self-classicying MNIST Digits ([Randazzo et al. (2020)](https://distill.pub/2020/selforg/mnist/) )
- [image_segmentation.py](/examples/image_segmentation.py)/[image_segmentation_hydra.py](/examples/image_segmentation_hydra.py) - NCA that can segment an image (with and without hydra) ([Sandler et al. (2020)](https://arxiv.org/abs/2008.04965))
- [genome_nca.py](/examples/genome_nca.py) - NCA that can be seeded with different genomes ([Stovold (2023)](https://arxiv.org/abs/2305.12971))


## Development

This project uses [uv](https://docs.astral.sh/uv/) for package management and distribution.

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/dwoiwode/ncalib.git
cd ncalib

# Install dependencies with uv
uv sync

# Install extra dependencies
uv sync  --all-extras
```

### Running Tests

Tests are run using pytest:

```bash
uv run pytest tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [PyPI Package](https://pypi.org/project/ncalib/)
- [GitHub](https://github.com/dwoiwode/ncalib)
- [Issues](https://github.com/dwoiwode/ncalib/issues)
# DLWheel

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)]()

A lightweight deep learning library.

## Installation

### Editable Installation

```bash
pip install -e .
```

### Stable Release

```bash
pip install dlwheel
```

## Getting Started

### Basic Usage

```python
from pprint import pprint

import dlwheel

cfg = dlwheel.setup()
pprint(cfg)
```

### Backup System

Use the `--backup` flag to enable automatic backup (stored in `./log` by default):

```bash
python main.py --backup
```

### Configuration System

#### YAML Config File (config/default.yaml):

```yaml
# config/default.yaml
lr: 1e-3
batch_size: 32
```

#### Command-Line Argument Override

```bash
python main.py --config=config/exp.yaml --name=exp batch_size=2 lr=0.1
```

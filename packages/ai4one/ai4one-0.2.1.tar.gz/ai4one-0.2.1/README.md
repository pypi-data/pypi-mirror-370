
# AI4One 🤖

A small, modular package for machine learning.

---

## Installation


```bash
pip install ai4one
````

This package requires **Python 3.8** or newer.

-----

## Usage

### ai4one.config
The primary feature of this package is a powerful configuration system. For a comprehensive guide and examples, please see the **[Configuration System Guide](docs/config.md)**.

```python
from ai4one.config import BaseConfig, field
from typing import List

class TrainConfig(BaseConfig):
    learning_rate: float = 0.001
    epochs: int = 10
    optimizer: str = "Adam"
    layers: List[int] = [3, 3]

if __name__ == "__main__":
    config = TrainConfig.argument_parser()
    print(f"Using optimizer: {config.optimizer}")
```

You can also run the self-contained example to see it in action:

```bash
examples/example_config.py
```

-----


### ai4one.cli

```bash
ai4one gpu
```

Outputs:
```
--- CUDA Version ---
12.7 

--- PyTorch Version ---
2.1.0+cu121

--- Python Version ---
Python 3.10.12

--- Python Executable Path ---
/usr/bin/python
```


## Development

Interested in contributing? Set up your local development environment with `uv`.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/bestenevoy/ai4one.git
    cd ai4one
    ```

2.  **Create a virtual environment and install dependencies:**
    This command installs all core, optional, and development dependencies.

    ```bash
    uv pip install -e ".[dev]"
    ```

    To keep your environment in sync with the lock file, you can run `uv sync`.

3.  **Run tests:**

    ```bash
    uv run pytest
    ```

-----

## Build and Publish

These commands are for package maintainers.

**Build the package:**

```bash
uv build
```

**Publish to PyPI:**

```bash
uv run twine upload dist/*
```

# Ryn SDK

A unified Python SDK for **data**, **model**, and **trainer** workflows.  
This repository mirrors the automatic release workflow used in `model-registry` (auto-publish to PyPI via GitHub Actions).

> **Default install pulls everything.** Subsets are available via extras (`ryn[model]`, `ryn[data]`, `ryn[trainer]`).

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Requirements Layout](#requirements-layout)
- [Versioning & Auto-Publish to PyPI](#versioning--auto-publish-to-pypi)
- [Local Development](#local-development)
- [Update Checker (Optional)](#update-checker-optional)
- [Supported Python Versions](#supported-python-versions)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

> **Default (everything):** installs the union of data + model + trainer requirements.

```bash
# Everything
pip install ryn

# Only the model stack
pip install "ryn[model]"

# Only the data stack
pip install "ryn[data]"

# Only the trainer stack
pip install "ryn[trainer]"
```

**Notes**

- Some dependencies (e.g., `torch`) may require platform-specific wheels. If you're on a GPU machine, consult the official PyTorch install guide for your CUDA/ROCm toolkit.
- If you need a slim install instead, use a virtual environment and install only the extras you need.

---

## Quick Start

```python
import ryn
from ryn import data, model, trainer

print("Ryn version:", ryn.__version__)

# Example scaffolding (replace with your actual API calls):
# Dataset operations
# ds = data.load_dataset("your-dataset-id")
# df = data.to_pandas(ds)

# Model registry / storage operations
# model_id = model.register_model(name="my-model", version="1.0.0", metadata={"task": "classification"})
# meta = model.get_model(name="my-model", version="1.0.0")

# Training utilities
# run = trainer.train(config={"epochs": 10, "lr": 1e-3})
# metrics = trainer.evaluate(run)
```
> The snippet above shows typical entry points. Replace with your actual functions/classes provided by `ryn.data`, `ryn.model`, and `ryn.trainer` in this repo.

---

## Project Structure

```
ryn/
  data/       # Data utilities & loaders
  model/      # Model registry / storage / inference helpers
  trainer/    # Training loops, trackers, and helpers
  __init__.py # Exposes public API and package metadata
```

---

## Requirements Layout

Dependencies are split into three groups under `requirements/` and combined for the default install:

```
requirements/
  model.txt    # e.g., boto3, huggingface-hub, transformers, einops, ...
  data.txt     # e.g., numpy, pandas, scikit-learn, datasets, openml, ...
  trainer.txt  # e.g., torch, torchvision, timm, albumentations, ...
```

- **Default install (`pip install ryn`)** = **union(model + data + trainer)**.
- Extras for explicit subsets:
  - `ryn[model]`
  - `ryn[data]`
  - `ryn[trainer]`

These groups are wired in `setup.py` so that PyPI metadata carries the dependency info.

---

## Versioning & Auto-Publish to PyPI

The repository uses a CI workflow (GitHub Actions) that **auto-bumps and publishes** to PyPI on **push to `main`** when the following conditions are met:

1. Repository variable **`PUBLISH_TO_PYPI`** is set to `true`.
2. The **commit message** contains the phrase **`pipy commit -push`**.

**Bump level** is controlled via the commit message:

- `pipy commit -push major` → bump **MAJOR**
- `pipy commit -push minor` → bump **MINOR**
- `pipy commit -push` (no keyword) → bump **PATCH** (default)

**Workflow outline**

1. Read current version from PyPI.
2. Compute next version (patch/minor/major).
3. Update `ryn/__init__.py` and `setup.py`.
4. Build distributions (`sdist` + `wheel`).
5. Upload to PyPI using Twine.

**Required repo settings**

- **Settings → Secrets and variables → Actions → Secrets**
  - `PYPI_API_TOKEN` (PyPI token)
- **Settings → Secrets and variables → Actions → Variables**
  - `PUBLISH_TO_PYPI = true`

---

## Local Development

```bash
# Clone
git clone https://github.com/AIP-MLOPS/rayen.git
cd rayen

# (Optional) Create a virtual environment
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode with a subset of extras, e.g., model
pip install -e ".[model]"

# Build locally
python -m pip install --upgrade pip build twine
python -m build
twine check dist/*
```

> If you prefer a full dev install, use `pip install -e ".[all]"` (identical to default deps).

---

## Update Checker (Optional)

The package may include a lightweight update checker that prints a hint if a newer version is available on PyPI. This check is best-effort and should never fail your import due to network issues.

---

## Supported Python Versions

- **Python 3.11+**

---

## Contributing

1. Fork the repository and create a feature branch.
2. Keep commits focused and meaningful.
3. Open a Pull Request with a clear description and, if applicable, tests or examples.

> Consider running your linter/formatter locally (e.g., `ruff`) before opening a PR.

---

## License

MIT

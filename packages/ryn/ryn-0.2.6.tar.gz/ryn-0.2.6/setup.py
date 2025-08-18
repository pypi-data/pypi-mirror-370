# setup.py
# - Default install installs ALL dependencies from requirements/ (your requested behavior).
# - extras_require defines subsets for optional installs (model, data, trainer).
# - "ryn[all]" is equivalent to the default full install.

from __future__ import annotations
from pathlib import Path
from setuptools import setup, find_packages


def read_meta() -> tuple[str | None, str | None]:
    """Read __version__ and __description__ from ryn/__init__.py."""
    init_path = Path("ryn/__init__.py")
    version = None
    description = None
    if init_path.exists():
        for line in init_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("__version__"):
                version = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("__description__"):
                description = line.split("=", 1)[1].strip().strip('"').strip("'")
    return version, description


def read_requirements(path: str) -> list[str]:
    """Read a requirements file (supports comments, empty lines, and nested -r)."""
    p = Path(path)
    if not p.exists():
        return []
    reqs: list[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):  # handle nested requirements
            nested = line.split(maxsplit=1)[1]
            reqs.extend(read_requirements(nested))
            continue
        reqs.append(line)
    return reqs


# Load requirements groups
model_reqs   = read_requirements("requirements/model.txt")
data_reqs    = read_requirements("requirements/data.txt")
trainer_reqs = read_requirements("requirements/trainer.txt")

# Default install = EVERYTHING
all_reqs = sorted(set(model_reqs + data_reqs + trainer_reqs))

# Optional subsets
extras = {
    "model": model_reqs,
    "data": data_reqs,
    "trainer": trainer_reqs,
    "all": all_reqs,  # ryn[all] == default
}

# Load version and description from __init__.py
version, description = read_meta()
readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else (description or "")

setup(
    name="ryn",
    version="0.2.6",
    description=description,
    author="AIP MLOPS Team",
    author_email="mohmmadweb@gmail.com",
    url="https://github.com/AIP-MLOPS/rayen",
    packages=find_packages(include=["ryn", "ryn.*"]),
    install_requires=all_reqs,   # default install installs everything
    extras_require=extras,       # ryn[model], ryn[data], ryn[trainer], ryn[all]
    python_requires=">=3.8",     # support wider Python versions
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

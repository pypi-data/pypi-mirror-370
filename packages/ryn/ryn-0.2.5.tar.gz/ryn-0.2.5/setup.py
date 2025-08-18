# setup.py
# - All dependencies are installed by default with install_requires.
# - extras_require defines specific dependencies for model, data, and trainer.
# - "ryn[all]" installs all extras combined.

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
    """Read a requirements file and return clean items (supports comments/empty lines and nested -r)."""
    p = Path(path)
    if not p.exists():
        return []
    reqs: list[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):  # nested requirements, e.g., -r requirements/extra.txt
            nested = line.split(maxsplit=1)[1]
            reqs.extend(read_requirements(nested))
            continue
        reqs.append(line)
    return reqs


# Read groups
model_reqs   = read_requirements("requirements/model.txt")
data_reqs    = read_requirements("requirements/data.txt")
trainer_reqs = read_requirements("requirements/trainer.txt")

# DEFAULT install = EVERYTHING (your requested behavior)
all_reqs = sorted(set(model_reqs + data_reqs + trainer_reqs))

# Extras just document subsets (they do NOT subtract defaults)
extras = {
    "model": model_reqs,
    "data": data_reqs,
    "trainer": trainer_reqs,
    "all": all_reqs,  # optional: ryn[all] same as default install
}

version, description = read_meta()
readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else (description or "")

setup(
    name="ryn",
    version="0.2.5",  # hard-coded on purpose; your CI updates this and ryn/__init__.py
    description=description or "Ryn SDK: data, model, and trainer interfaces",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="AIP MLOPS Team",
    author_email="mohmmadweb@gmail.com",
    url="https://github.com/AIP-MLOPS/rayen",
    packages=find_packages(include=["ryn", "ryn.*"]),
    install_requires=all_reqs,   # <-- installs EVERYTHING on plain `pip install ryn`
    extras_require=extras,       # <-- ryn[model], ryn[data], ryn[trainer], ryn[all]
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

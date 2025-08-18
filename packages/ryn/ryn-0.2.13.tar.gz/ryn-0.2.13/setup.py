from setuptools import setup, find_packages
from pathlib import Path

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

# Define all dependencies
data_reqs = [
    'numpy',
    'pandas',
    'scikit-learn',
    'datasets',
    'openml',
    'kagglehub',
    'python-dotenv',
]

model_reqs = [
    'timm',
    'albumentations',
    'huggingface_hub',
    'einops',
    'boto3',
    'tqdm',
    'tabulate',
    'requests',
    'python-dotenv',
]

trainer_reqs = [
    'torch',
    'torchvision',
    'tensorboard',
    'clearml',
    'tqdm',
    'reformer-pytorch',
    'sktime',
    'PyWavelets',
]

all_reqs = sorted(set(data_reqs + model_reqs + trainer_reqs))

extras = {
    "model": model_reqs,
    "data": data_reqs,
    "trainer": trainer_reqs,
    "all": all_reqs,
}

version, description = read_meta()
readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else (description or "")

setup(
    name="ryn",
    version="0.2.13",
    description=description,
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    author="AIP MLOPS Team",
    author_email="mohmmadweb@gmail.com",
    url="https://github.com/AIP-MLOPS/rayen",
    packages=find_packages(include=["ryn", "ryn.*"]),
    install_requires=all_reqs,
    extras_require=extras,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
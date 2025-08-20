from setuptools import setup, find_packages
from pathlib import Path

__version__ = "0.0.4"
__author__ = "Igor Borja"
__email__ = "igorpradoborja@gmail.com"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(
    Path(__file__).parent / "dependencies" / "frozen_requirements.txt",
    "r",
    encoding="utf-8",
) as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="pathology_foundation_models",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Interface for calling foundation models for histopathology image analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IgorPBorja/pathology-foundation-models",
    packages=find_packages(exclude=["tests", "experiments"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "notebook": [
            "jupyter",
            "ipykernel",
            "ipywidgets",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line scripts here if needed
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)

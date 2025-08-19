#!/usr/bin/env python3
"""
Setup script for CogniCLI
"""

from setuptools import setup, find_packages


# Read the long description from README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read version from pyproject.toml
def get_version():
    import re
    with open("pyproject.toml", "r", encoding="utf-8") as fh:
        content = fh.read()
        match = re.search(r'version = "([^"]+)"', content)
        if match:
            return match.group(1)
    return "2.0.8"


setup(
    name="cognicli",
    version=get_version(),
    author="SynapseMoN",
    description="A premium, full-featured AI command line interface with Transformers and GGUF support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cognicli/cognicli",
    py_modules=["cognicli"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="ai,llm,transformers,gguf,huggingface,cli,chatbot,language-model,artificial-intelligence,machine-learning,natural-language-processing,text-generation,chat,assistant,premium,robust,enhanced",
    python_requires=">=3.8",
    install_requires=[
        "hf_xet",
        "transformers>=4.35.0",
        "huggingface-hub>=0.17.0",
        "rich>=13.0.0",
        "colorama>=0.4.6",
        "requests>=2.31.0",
        "psutil>=5.9.0",
        "pyyaml>=6.0",
        "numpy>=1.24.0",
        "tokenizers>=0.14.0",
        "accelerate>=0.24.0",
        "sentencepiece>=0.1.99",
        "protobuf>=4.24.0",
        "ollama>=0.1.0",
    ],
    extras_require={
        "quantization": ["bitsandbytes>=0.41.0"],
        "gguf": ["llama-cpp-python>=0.2.0"],
        "gpu": [
            "bitsandbytes>=0.41.0",
            "llama-cpp-python[cublas]>=0.2.0",
        ],
        "metal": [
            "bitsandbytes>=0.41.0",
            "llama-cpp-python[metal]>=0.2.0",
        ],
        "full": [
            "bitsandbytes>=0.41.0",
            "llama-cpp-python>=0.2.0",
            "datasets>=2.14.0",
            "evaluate>=0.4.0",
            "wandb>=0.15.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cognicli=cognicli:main",
            "cog=cognicli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

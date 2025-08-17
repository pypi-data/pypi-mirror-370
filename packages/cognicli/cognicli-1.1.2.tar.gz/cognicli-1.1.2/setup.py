from setuptools import setup, find_packages
import sys

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Check Python version
if sys.version_info < (3, 8):
    raise RuntimeError("CogniCLI requires Python 3.8 or higher")

setup(
    name="cognicli",
    version="1.1.2",
    author="SynapseMoN",
    description="A full-featured, premium AI command line interface with Transformers and GGUF support",
    long_description=long_description,
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
    python_requires=">=3.8",
    install_requires=[
        "hf_xet",
        "torch>=2.0.0",
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
    },
    entry_points={
        "console_scripts": [
            "cognicli=cognicli:main",
            "cog=cognicli:main",
        ],
    },
    keywords=[
        "ai", "llm", "transformers", "gguf", "huggingface", "cli", "chatbot",
        "language-model", "artificial-intelligence", "machine-learning",
        "natural-language-processing", "text-generation", "chat", "assistant"
    ],
    project_urls={
        "Bug Reports": "https://github.com/cognicli/cognicli/issues",
        "Source": "https://github.com/cognicli/cognicli",
        "Documentation": "https://cognicli.readthedocs.io",
    },
    zip_safe=False,
    include_package_data=True,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="naganlp",
    version="0.1.0",  # This will be overridden by setuptools_scm if enabled
    author="Agniva Maiti",
    author_email="maitiagniva@gmail.com",
    description="A Natural Language Processing toolkit for the Nagamese creole",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AgnivaMaiti/naga-nlp",
    project_urls={
        "Bug Reports": "https://github.com/AgnivaMaiti/naga-nlp/issues",
        "Source": "https://github.com/AgnivaMaiti/naga-nlp",
        "Documentation": "https://github.com/AgnivaMaiti/naga-nlp#readme",
    },
    packages=find_packages(exclude=["tests*"]),
    package_data={
        "naganlp": [
            "py.typed",
            "*.model",
            "*.pkl",
            "*.conll"
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    keywords="nlp nlp-library nlp-machine-learning nagamese-language",

    # Enable setuptools_scm for versioning
    use_scm_version={
        "write_to": "naganlp/_version.py",
        "write_to_template": "__version__ = '{version}'",
    },
    setup_requires=["setuptools_scm"],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "naganlp=naganlp.cli:main",
        ],
    },
    zip_safe=False,
)

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from _version.py
version = {}
with open(os.path.join(this_directory, 'cellproportion', '_version.py')) as f:
    exec(f.read(), version)

setup(
    name="cellproportion",
    version=version['__version__'],
    author="Ankit Patel",
    author_email="ankit.patel@qmul.ac.uk",
    description="Cell type proportion analysis for single-cell and spatial transcriptomics data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ankitpatel/cellproportion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "statsmodels>=0.12.0",
        "anndata>=0.8.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "sphinx",
            "sphinx-rtd-theme"
        ]
    },
    keywords=[
        "single-cell",
        "spatial-transcriptomics", 
        "cell-type-analysis",
        "proportion-analysis",
        "bioinformatics",
        "genomics",
        "scRNA-seq"
    ],
    project_urls={
        "Bug Reports": "https://github.com/ankitpatel/cellproportion/issues",
        "Source": "https://github.com/ankitpatel/cellproportion",
        "Documentation": "https://cellproportion.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)

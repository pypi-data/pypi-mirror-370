# setup.py
import os
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="trustra",
    version="1.0.0",
    description="Trust-first AutoML: Automated ML with built-in fairness, drift, and reliability.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Devansh Singh",
    author_email="devansh.jay.singh@gmail.com",
    url="https://github.com/Devansh-567/Trustra---Trust-First-AutoML-Framework",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5",
        "numpy>=1.21",
        "scikit-learn>=1.3",
        "optuna>=3.0",
        "plotly>=5.10",
        "jinja2>=3.1",
        "fairlearn>=0.10",
        "xgboost>=1.7"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.9",
    keywords="automl, fairness, bias, drift, explainability, machine-learning, responsible-ai",
    project_urls={
        "Documentation": "https://github.com/Devansh-567/Trustra---Trust-First-AutoML-Framework#readme",
        "Source": "https://github.com/Devansh-567/Trustra---Trust-First-AutoML-Framework",
        "Tracker": "https://github.com/Devansh-567/Trustra---Trust-First-AutoML-Framework/issues",
    },
    include_package_data=True,
)
#!/usr/bin/env python3
"""Setup script for simpleKG package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from Pipfile (convert to requirements.txt format)
install_requires = [
    "dspy-ai>=2.6.24",
    "openai>=1.61.0",
    "numpy<2",
    "pydantic>=2.0.0",
    "sentence-transformers",
    "scikit-learn",
    "python-dotenv",
    "concurrent-futures; python_version<'3.2'",
]

dev_requires = [
    "pyvis>=0.3.2",
    "ipywidgets",
    "jupyter",
    "pytest",
    "pytest-cov",
    "black",
    "flake8",
]

setup(
    name="simplekg",
    version="0.1.0",
    author="Hadar Miller",
    author_email="your.email@example.com",  # Replace with your email
    description="Knowledge Graph generation from Hebrew text using OpenAI GPT models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["knowledge-graph", "hebrew", "nlp", "openai", "gpt", "entity-extraction", "ontology", "skos", "text-analysis", "ai"],
    url="https://gitlab.com/millerhadar/simplekg",
    project_urls={
        "Bug Tracker": "https://gitlab.com/millerhadar/simplekg/-/issues",
        "Documentation": "https://gitlab.com/millerhadar/simplekg/-/blob/main/README.md",
        "Source Code": "https://gitlab.com/millerhadar/simplekg",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "visualization": ["pyvis>=0.3.2"],
        "jupyter": ["ipywidgets", "jupyter"],
    },
    include_package_data=True,
    package_data={
        "simplekg": [
            "ontologies.txt",
            "documentation.txt",
            "*.html",
        ],
    },
    entry_points={
        "console_scripts": [
            "simplekg=simplekg.cli:main",  # We'll create this later
        ],
    },
    zip_safe=False,
)

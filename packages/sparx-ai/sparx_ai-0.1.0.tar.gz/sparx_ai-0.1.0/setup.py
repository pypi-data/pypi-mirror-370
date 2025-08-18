from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sparx-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A collection of Generative AI code examples and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sparx-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "matplotlib",
        "scikit-learn",
        "scipy",
        "tensorflow",
        "torch",
        "spacy",
        "sentence-transformers",
        "transformers",
        "faiss-cpu",
        "pandas",
    ],
    include_package_data=True,
    package_data={
        "sparx": ["data/*.txt"],
    },
)

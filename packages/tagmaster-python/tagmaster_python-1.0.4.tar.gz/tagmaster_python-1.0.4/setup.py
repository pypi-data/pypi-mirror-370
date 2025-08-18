from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README_PYTHON_CLIENT.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tagmaster-python",
    version="1.0.4",
    author="Tagmaster",
    author_email="support@tagmaster.com",
    description="A Python client for the Tagmaster classification API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tagmaster/tagmaster-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    keywords="tagmaster, classification, api, client, text-analysis, nlp",
    project_urls={
        "Bug Reports": "https://github.com/tagmaster/tagmaster-python/issues",
        "Source": "https://github.com/tagmaster/tagmaster-python",
        "Documentation": "https://github.com/tagmaster/tagmaster-python#readme",
    },
    include_package_data=True,
    zip_safe=False,
) 
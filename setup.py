"""
Setup script for ZAPI - maintained for backwards compatibility.
Prefer using pyproject.toml for modern Python packaging.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zapi",
    version="0.1.0",
    author="ZAPI Contributors",
    description="Zero-Config API Intelligence - automatically discover, understand, and prepare APIs for LLM and agent workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adoptai/zapi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "playwright>=1.40.0",
    ],
    keywords="api llm automation browser network har",
)

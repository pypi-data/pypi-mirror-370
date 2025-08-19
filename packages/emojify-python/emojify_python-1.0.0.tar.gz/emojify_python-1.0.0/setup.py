#!/usr/bin/env python
"""Setup script for emojify-python package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="emojify-python",
    version="1.0.0",
    author="Arpan Ghoshal",
    author_email="contact@arpanghoshal.com",
    description="The Ultimate Emoji Programming Experience - Import modules, write operators, create classes with emojis! 🐍✨",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arpanghoshal/emojify-python",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0;python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.990",
            "hypothesis>=6.0",
        ],
        "jupyter": [
            "ipython>=8.0",
            "jupyter>=1.0",
        ]
    },
    keywords="emoji import fun python programming emojify unicode ast transformation metaprogramming",
    project_urls={
        "Bug Reports": "https://github.com/arpanghoshal/emojify-python/issues",
        "Source": "https://github.com/arpanghoshal/emojify-python",
        "Documentation": "https://emojify-python.readthedocs.io",
    },
    entry_points={
        "console_scripts": [
            "emoji-python=emojify_python.__main__:main",
        ],
    },
)
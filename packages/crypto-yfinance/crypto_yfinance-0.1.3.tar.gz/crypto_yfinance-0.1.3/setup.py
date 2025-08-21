from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""

setup(
    name="crypto-yfinance",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "ccxt",
        "pycoingecko",
        "matplotlib",
        "pandas",
        "plotly",
    ],
    author="Aakash Chavan Ravindranath",
    author_email="craakash@gmail.com",
    description="Unified cryptocurrency data API like yfinance",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://medium.com/@craakash",
    project_urls={
        "LinkedIn": "https://www.linkedin.com/in/aakashcr/",
        "Source": "https://github.com/craakash/cryptofinance",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license="MIT",
    license_files=[],  # disable License-File metadata completely
)
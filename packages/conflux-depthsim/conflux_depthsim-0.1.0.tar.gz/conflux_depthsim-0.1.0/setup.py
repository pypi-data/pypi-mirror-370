#!/usr/bin/env python3
"""
DepthSim - Order Book Depth Simulation Package

Professional-grade order book depth simulation for backtesting and market analysis.
Designed to consume market data from MockFlow or other sources and synthesize
realistic bid-ask spreads, order book depth, and trade prints.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="conflux-depthsim",
    version="0.1.0",
    author="Conflux ML Engine Team",
    author_email="noreply@conflux-ml.com",
    description="Professional order book depth simulation for backtesting and market analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefan-mcf/depthsim",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "matplotlib>=3.5.0",
            "jupyter>=1.0.0",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords="trading, backtesting, order-book, market-data, depth, simulation, finance, algorithmic-trading",
    project_urls={
        "Bug Reports": "https://github.com/stefan-mcf/depthsim/issues",
        "Source": "https://github.com/stefan-mcf/depthsim",
        "Documentation": "https://github.com/stefan-mcf/depthsim#readme",
    },
)
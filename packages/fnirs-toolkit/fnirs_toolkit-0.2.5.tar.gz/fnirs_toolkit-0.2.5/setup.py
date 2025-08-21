from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取 requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fnirstoolkit",
    version="0.2.5",
    author="Jamie, Wendy",
    author_email="zhouyang.xu@youguo.com",
    description="A comprehensive Python package for fNIRS data analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xzywisdili/fNIRSAnalysisProcess",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    package_data={
        "fnirs_toolkit": [
            "data/*.txt",
            "data/*.json",
            "data/*.csv",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "fnirs-process=fnirs_toolkit.cli:main",
        ],
    },
    keywords="fnirs, neuroimaging, signal processing, hemodynamics, brain imaging",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fnirs-toolkit/issues",
        "Source": "https://github.com/yourusername/fnirs-toolkit",
        "Documentation": "https://fnirs-toolkit.readthedocs.io/",
    },
)
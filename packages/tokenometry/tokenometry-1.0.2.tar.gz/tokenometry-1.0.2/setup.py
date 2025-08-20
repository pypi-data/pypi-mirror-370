from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements.txt for dependencies
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tokenometry",
    version="1.0.2",
    author="nguyenph88",
    author_email="your.email@example.com",  # Update this with your actual email
    description="A sophisticated multi-strategy crypto analysis bot for trading signals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nguyenph88/Tokenometry",
    project_urls={
        "Bug Tracker": "https://github.com/nguyenph88/Tokenometry/issues",
        "Documentation": "https://github.com/nguyenph88/Tokenometry#readme",
        "Source Code": "https://github.com/nguyenph88/Tokenometry",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "build>=0.7",
        ],
    },
    keywords="cryptocurrency, trading, analysis, bot, signals, technical-analysis, crypto, bitcoin, ethereum",
    include_package_data=True,
    zip_safe=False,
)

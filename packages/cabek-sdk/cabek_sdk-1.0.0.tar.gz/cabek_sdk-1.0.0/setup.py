"""
Setup configuration for C.A.B.E.K. Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cabek-sdk",
    version="1.0.0",
    author="C.A.B.E.K. Technologies",
    author_email="developers@cabek.io",
    description="Official Python SDK for C.A.B.E.K. biometric authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cabek-tech/cabek-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ecg": [
            "scipy>=1.9.0",
            "scikit-learn>=1.2.0",
            "biosppy>=0.8.0",  # For advanced ECG processing
        ]
    },
    entry_points={
        "console_scripts": [
            "cabek-test=cabek_sdk:example_usage",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/cabek-tech/cabek-python-sdk/issues",
        "Documentation": "https://docs.cabek.io/sdk/python",
        "Source": "https://github.com/cabek-tech/cabek-python-sdk",
    },
)

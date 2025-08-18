"""
MAOS - Multi-Agent Orchestration System
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="maos",
    version="1.0.0",
    author="MAOS Contributors",
    author_email="support@maos.dev",
    description="Multi-Agent Orchestration System - True parallel AI agent execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/maos",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "asyncio>=3.4.3",
        "redis>=5.0.0",
        "aioredis>=2.0.0",
        "pydantic>=2.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "prometheus-client>=0.19.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
        "boto3>=1.34.0",
        "networkx>=3.2",
        "numpy>=1.24.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pre-commit>=3.5.0",
        ],
        "monitoring": [
            "grafana-api>=1.0.3",
            "prometheus-client>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "maos=maos.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "maos": ["config/*.yaml", "config/*.json"],
    },
    zip_safe=False,
)
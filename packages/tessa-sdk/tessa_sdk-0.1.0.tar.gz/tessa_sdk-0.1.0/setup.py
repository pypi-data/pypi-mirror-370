"""Setup script for tessa_sdk package."""

from setuptools import setup, find_packages

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tessa_sdk",
    version="0.1.0",
    author="Tessa Team",
    author_email="support@generalagency.ai",
    description="Python SDK for the Tessa Browser Agent & Workflows API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeneralAgencyAI/tessa_sdk",
    packages=find_packages(include=["tessa_sdk*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.5.0;python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ]
    },
    project_urls={
        "Homepage": "https://heytessa.ai",
        "Documentation": "https://docs.heytessa.ai",
        "Repository": "https://github.com/GeneralAgencyAI/tessa_sdk",
        "Issues": "https://github.com/GeneralAgencyAI/tessa_sdk/issues",
    },
)

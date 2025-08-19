"""
Setup script for dolfi-python-sdk package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dolfi-python-sdk",
    version="1.0.0",
    author="Dolfi SDK Team",
    author_email="support@dolfi.com",
    description="Python SDK for the Dolfi API - search and web scraping made simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dolfi/dolfi-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/dolfi/dolfi-python-sdk/issues",
        "Documentation": "https://docs.dolfi.com",
        "Homepage": "https://dolfi.com",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    keywords=[
        "dolfi",
        "api",
        "sdk",
        "search",
        "web scraping",
        "scraping",
        "web",
        "content extraction",
        "ai search",
        "natural language search",
    ],
    license="MIT",
    zip_safe=False,
    include_package_data=True,
)
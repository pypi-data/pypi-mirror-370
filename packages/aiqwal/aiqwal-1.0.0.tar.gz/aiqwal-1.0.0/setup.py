# setup.py - Main package configuration
"""
AIQWAL - AI Query Writer for Any Language
A universal AI-powered SQL generator that works with ANY database
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "AI Query Writer for Any Language - Universal SQL generator"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "llama-cpp-python>=0.2.0",
            "sqlalchemy>=2.0.0",
            "psycopg2-binary",  # PostgreSQL
            "pymysql",          # MySQL
            "pyodbc",           # SQL Server
            "cx-oracle",        # Oracle
            "snowflake-sqlalchemy",  # Snowflake
            "pybigquery",       # BigQuery
            "redshift-connector", # Redshift
        ]

setup(
    name="aiqwal",
    version="1.0.0",
    author="Shivnath tathe",
    author_email="sptathe2001@gmail.com",
    description="AI Query Writer for Any Language - Universal SQL generator that works with ANY database",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shivnathtathe/aiqwal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "all": [
            # All database drivers
            "psycopg2-binary",
            "pymysql", 
            "pyodbc",
            "cx-oracle",
            "snowflake-sqlalchemy",
            "pybigquery",
            "redshift-connector",
            "pymongo",  # MongoDB
        ]
    },
    entry_points={
        "console_scripts": [
            "aiqwal=aiqwal.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "aiqwal": [
            "models/*.gguf",
            "configs/*.json",
            "templates/*.sql",
        ],
    },
    zip_safe=False,
    keywords="ai sql database natural-language llm sqlalchemy query-generator",
    # project_urls={
    #     "Bug Reports": "https://github.com/yourusername/aiqwal/issues",
    #     "Source": "https://github.com/yourusername/aiqwal",
    #     "Documentation": "https://aiqwal.readthedocs.io/",
    # },
)
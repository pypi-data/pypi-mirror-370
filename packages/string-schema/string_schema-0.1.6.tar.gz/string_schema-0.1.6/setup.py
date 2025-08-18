"""
Setup script for String Schema package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="string-schema",
    version="0.1.6",
    author="Michael Chen",
    author_email="xychen@msn.com",
    description="A simple, LLM-friendly schema definition library for converting string syntax to structured schemas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xychenmsn/string-schema",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0.0",
        "email-validator>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    keywords="schema validation json llm ai data-extraction",
    project_urls={
        "Bug Reports": "https://github.com/xychenmsn/string-schema/issues",
        "Source": "https://github.com/xychenmsn/string-schema",
        "Documentation": "https://github.com/xychenmsn/string-schema#readme",
    },
)

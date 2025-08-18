from setuptools import setup, find_packages
import re
from pathlib import Path

def get_version():
    """Get the version from __init__.py"""
    init_file = Path("helpr/__init__.py").read_text()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version string not found in __init__.py")

def read_file(file):
    """Read a file and return its content."""
    try:
        with open(file, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

# Runtime dependencies - these are the only ones that will be installed with the package
install_requires = [
    "boto3>=1.35.81",
    "botocore>=1.35.81",
    "fastapi>=0.115.6",
    "redis>=4.5.0",
    "Authlib>=1.2.0",
    "pydantic==2.10.2",
    "typing_extensions>=4.12.2",
    "structlog==25.4.0",
    "phonenumbers==9.0.5",
    "sqlalchemy>=1.4.0",
    "psycopg2-binary>=2.9.0",
]

setup(
    name="helpr",
    version=get_version(),
    author="Clinikally",
    author_email="dev@clinikally.com",
    description="A utility package for Clinikally applications",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/clinikally/helpr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=install_requires,
)
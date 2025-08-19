from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gava_connect",
    version="1.0.0",
    author="Paul Ndambo",
    author_email="paulkadabo@gmail.com",
    description="A Python package for simplified access to Kenya Revenue Authority (KRA) API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Paulndambo/KRA-Gava-Connect",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    keywords="kra, kenya, revenue, authority, api, tax, pin, gava, connect",
    project_urls={
        "Bug Reports": "https://github.com/Paulndambo/KRA-Gava-Connect/issues",
        "Source": "https://github.com/Paulndambo/KRA-Gava-Connect",
        "Documentation": "https://github.com/Paulndambo/KRA-Gava-Connect#readme",
    },
)

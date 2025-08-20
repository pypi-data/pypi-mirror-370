from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="guojiqe-sdk",
    version="0.0.0",
    author="CETC Guoji Quantum",
    author_email="yuanchenhao@tgqs.net",
    description="A Python SDK for interacting with Guoji Quantum and Electronic Computing Service Platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guojiquantum/guojiqe-sdk",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.9",
    install_requires=[
        "qiskit>=2.0.0",
    ],
    # extras_require={
    #     "dev": [
    #         "pytest>=6.0",
    #         "black",
    #         "flake8",
    #     ]
    # },
)
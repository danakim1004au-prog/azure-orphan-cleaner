# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
from setuptools import setup, find_packages

VERSION = "0.1.0"

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

DEPENDENCIES = [
    "azure-cli-core>=2.50.0",
    "azure-identity>=1.14.0",
    "azure-mgmt-resourcegraph>=8.0.0",
    "azure-mgmt-compute>=30.0.0",
    "azure-mgmt-network>=25.0.0",
    "azure-mgmt-web>=7.0.0",
    "knack>=0.10.0",
]

DEV_DEPENDENCIES = [
    "flake8>=6.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "build>=1.0.0",
    "twine>=4.0.0",
]

setup(
    name="azure-resource-sweeper",
    version=VERSION,
    description="Azure CLI extension to detect and safely clean up stale and unused resources.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Dana Kim",
    author_email="danakim1004.au@gmail.com",
    url="https://github.com/danakim1004au-prog/azure-resource-sweeper",
    license="Apache-2.0",
    classifiers=CLASSIFIERS,
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=DEPENDENCIES,
    extras_require={"dev": DEV_DEPENDENCIES},
    include_package_data=True,
    # Azure CLI discovers extensions through this entry-point group.
    # The group name MUST be "azure.cli.extensions" for azdev and the CLI to
    # recognize the package as a first-class extension.
    entry_points={
        "azure.cli.extensions": [
            "resource-sweeper = azext_resource_sweeper",
        ],
    },
)

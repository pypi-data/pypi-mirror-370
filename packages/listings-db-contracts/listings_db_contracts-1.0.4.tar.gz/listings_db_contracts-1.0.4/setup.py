#!/usr/bin/env python3
"""
Setup script for listings_db_contracts package.
"""

from setuptools import setup, find_packages

setup(
    name="listings-db-contracts",
    version="1.0.0",
    description="Data contracts for the Finder property listings application",
    author="giacomokavanagh",
    author_email="giacomokavanagh@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0",
    ],
    include_package_data=True,
) 
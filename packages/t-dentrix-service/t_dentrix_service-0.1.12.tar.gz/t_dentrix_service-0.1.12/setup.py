#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

install_requirements = open("requirements.txt").readlines()

setup(
    author="Thoughtful",
    author_email="support@thoughtful.ai",
    python_requires=">=3.11.5",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    description="Service for handling Dentrix processes.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="t_dentrix_service",
    name="t_dentrix_service",
    packages=find_packages(include=["t_dentrix_service", "t_dentrix_service.*"]),
    test_suite="tests",
    url="https://www.thoughtful.ai/",
    version="0.1.12",
    zip_safe=False,
    install_requires=install_requirements,
)

from __future__ import annotations

from setuptools import find_packages, setup


def find_required():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="custom-otello-linter",
    version="1.0.5",
    description="flake8 based linter for frontend tests",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    url="https://github.com/iri6e4k0/custom-otello-linter",
    author="Irina",
    author_email="iri6e4ko@gmail.com",
    license="Apache-2.0",
    packages=find_packages(exclude=("tests",)),
    package_data={"custom_otello_linter": ["py.typed"]},
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

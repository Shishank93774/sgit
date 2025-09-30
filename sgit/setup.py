from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="sgit",
    version="1.0.0",
    author="Shishank Rawat",
    author_email="shishank.rawat@gmail.com",
    description="Write Yourself A Git - A Python implementation of Git",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sgit=sgit.cli.main:main",
        ],
    },
)
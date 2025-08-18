from setuptools import setup, find_packages
import os
import sys


def get_requirements(path):
    with open(path) as f:
        return f.read().splitlines()


base_requirements = get_requirements(
    os.path.join("tms_integration", "requirements.txt")
)

# Define the requirements for each optional component
lis_winsped_requirements = get_requirements(
    os.path.join("tms_integration", "lis_winsped", "requirements.txt")
)
# Assuming carlo has its own requirements.txt
carlo_requirements = get_requirements(
    os.path.join("tms_integration", "carlo", "requirements.txt")
)

setup(
    name="tms_integration",
    version="0.1.4",
    description="A library for TMS integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="F-ONE Group",
    author_email="admin@f-one.group",
    url="https://github.com/F-ONE-Group/tms_integration/tree/pypi",
    packages=find_packages(exclude=["tests*"]),
    install_requires=base_requirements,
    extras_require={
        "lis_winsped": lis_winsped_requirements,
        "carlo": carlo_requirements,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

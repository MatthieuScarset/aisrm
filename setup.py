"""Setup configuration for the AISRM package."""

from setuptools import find_packages, setup

with open("requirements.txt", encoding="utf-8") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

with open(".env", encoding="utf-8") as f:
    content = f.readlines()
version = [x.split("=")[-1] for x in content if "TAG=" in x][0]

setup(
    name="aisrm",
    version=version,
    install_requires=requirements,
    packages=find_packages(),
)

"""
Defines the Python package setup for the dynamofl package.
"""
from pathlib import Path

from setuptools import find_namespace_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="dynamofl",
    version="0.2.0",
    author="Emile Indik",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests~=2.32.0",
        "websocket-client==1.5.0",
        "shortuuid==1.0.11",
        "tqdm==4.66.3",
        "dataclasses-json==0.6.7",
    ],
)

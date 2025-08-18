# setup.py
from setuptools import setup, find_packages

long_description = ""
# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="core_infinity_stones",
    version="0.0.30",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={"core_infinity_stones": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=[
        "annotated-types==0.7.0",
        "anyio==4.8.0",
        "certifi==2024.12.14",
        "h11==0.14.0",
        "httpcore==1.0.7",
        "httpx==0.28.1",
        "idna==3.10",
        "pydantic==2.10.6",
        "pydantic_core==2.27.2",
        "sniffio==1.3.1",
        "typing_extensions==4.12.2",
    ],
)

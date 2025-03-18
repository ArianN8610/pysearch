from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pseek",
    version="1.0.1",
    author="Arian",
    author_email="ariannasiri86@gmail.com",
    description="Pseek is a Python library to search files, folders, and text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArianN8610/pysearch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["click==8.1.8"],
    entry_points={"console_scripts": ["pseek=pseek.cli:search"]}
)

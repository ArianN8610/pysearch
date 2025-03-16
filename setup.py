from setuptools import setup, find_packages


setup(
    name="pysearch",
    version="1.0.0",
    author="Arian",
    author_email="ariannasiri86@gmail.com",
    description="Pysearch is a Python library to search files, folders, and text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ArianN8610/pysearch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["click==8.1.8"]
)

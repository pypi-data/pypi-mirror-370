from setuptools import setup, find_packages

setup(
    name="fileflix",
    version="0.1.3",
    description="A simple package to read and write multiple file formats with one function",
    author="Rajkumar Suryavanshi",
    author_email="krajsuryaaa@gmail.com",
    url="https://github.com/Suryavanshii/fileflix",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
        "pyarrow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
from setuptools import setup, find_packages

setup(
    name="retrocal",  # pick a unique name, PyPI requires uniqueness
    version="0.1.0",
    py_modules=["calculator"],  # since you only have calculator.py
    install_requires=[
        # List dependencies here, e.g. "numpy>=1.24.0"
    ],
    entry_points={
        "console_scripts": [
            "retrocal=retrocal.calculator:main",  # if you have a main() function for CLI
        ],
    },
    author="ben roshan",
    author_email="benroshan100@gmail.com",
    description="A simple calculator module for basic arithmetic operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # change if using another license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

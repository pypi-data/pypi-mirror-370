from setuptools import setup, find_packages

setup(
    name="stockpredictor",  # PyPI name (must be unique)
    version="0.2.2",        # Start with 0.1.0, update with each release
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "yfinance",
        "matplotlib",
        "scikit-learn"
    ],
    author="DeviprasadGurrana",
    author_email="deviprasadgurrana@gmail.com",
    description="A Python library for predicting stock index trends using historical data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DeviprasadGurrana/stockpredictor",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

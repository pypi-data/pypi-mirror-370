from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fitdistcp",
    version="0.0.0",
    author="Lynne Jewson",
    author_email="lynne.jewson@gmail.com",
    description="A Python package for making reliable predictions using calibrating priors.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lynnejewson/fitdistcp",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'matplotlib'
    ]
)
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="zipcode_features",
    version="0.0.1",
    description="A tool to get features based on census data from zipcodes",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/EricSchles/zipcode_features",
    author="Eric Schles",
    author_email="ericschles@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    packages=[
        "zipcode_features",
    ],
    include_package_data=True,
    install_requires=["zipcodes", "pandas"],
)

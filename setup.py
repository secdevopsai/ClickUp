import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clickup",
    version="0.0.6",
    author="Ronald Eddings",
    author_email="ron@secdevops.ai",
    description="A Python library for the ClickUp API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/secdevopsai/clickup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

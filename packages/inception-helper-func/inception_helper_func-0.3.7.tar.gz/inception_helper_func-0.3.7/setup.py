import os
from setuptools import setup, find_packages, Command


class CleanUpCommand(Command):
    """Custom command to remove files created by inception_helper_func."""

    description = "Clean up files created by inception_helper_func"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


setup(
    name="inception_helper_func",
    version="0.3.7",
    author="KhaduaBloom",
    author_email="khaduabloom@gmail.com",
    description="inception_helper_func is a package that contains helper functions for the InceptionForce project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KhaduaBloom/inceptionforcepackages/tree/main/PythonPackage/inceptionHelperFunc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.0",
    install_requires=[
        "graypy==2.1.0",
        "psutil==6.1.0",
        "pytz==2025.2",
        "fastapi",
        "aiohttp[speedups]",
        "sqlalchemy",
        "pymongo[srv]",
        "elasticsearch==8.17.2",
    ],
    cmdclass={
        "cleanup": CleanUpCommand,
    },
)

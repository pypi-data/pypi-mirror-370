import sys
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).resolve().parent

with Path.open(Path(HERE) / "README.md", encoding="utf-8") as f:
    long_description = f.read()

if sys.argv:
    if "broker_sdk" in set(sys.argv):
        sys.argv.remove("broker_sdk")
        setup(
            name="ul-data-logger-sdk",
            version="3.0.4",
            description="Data logger sdk",
            author="Unic-lab",
            long_description=long_description,
            long_description_content_type="text/markdown",
            packages=find_packages(include=["data_logger_sdk*"]),
            include_package_data=True,
            package_data={
                "": ["*.yml", "py.typed"],
                "data_logger_sdk": ["py.typed"],
            },
            license="MIT",
            classifiers=[
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Operating System :: OS Independent",
            ],
            platforms="any",
            install_requires=[
                "ul-unipipeline>=2.0.0",
                # "ul-data-aggregator-sdk>=8.13.2",
                # "ul-py-tool==2.1.3,
                # "ul-api-utils==8.1.9",
                # "ul-db-utils==4.0.2",
                # "ul-data-gateway-sdk==1.0.6",
            ],
        )
    elif "api_sdk" in set(sys.argv):
        sys.argv.remove("api_sdk")
        setup(
            name="ul-data-logger-api-sdk",
            version="2.0.2",
            description="Data logger API sdk",
            author="Unic-lab",
            long_description=long_description,
            long_description_content_type="text/markdown",
            packages=find_packages(include=["data_logger_api_sdk*"]),
            include_package_data=True,
            package_data={
                "": ["*.yml", "py.typed"],
                "data_logger_api_sdk": ["py.typed"],
            },
            license="MIT",
            classifiers=[
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Operating System :: OS Independent",
            ],
            platforms="any",
            install_requires=[
                "ul-unipipeline>=2.0.0",
                "tqdm==4.66.1",
                # "ul-data-aggregator-sdk>=8.13.2",
                # "ul-py-tool==2.1.4,
                # "ul-api-utils==9.1.1",
                # "ul-db-utils==5.1.0",
                # "ul-data-gateway-sdk==1.0.6",
            ],
        )

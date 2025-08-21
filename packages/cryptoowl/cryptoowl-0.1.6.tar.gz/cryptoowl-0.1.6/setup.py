from setuptools import setup, find_packages

with open("./README.md") as readme:
    long_description = readme.read()

setup(
    name="cryptoowl",
    version="0.1.6",
    author="Cryptoowl",
    author_email="cryptoowl.app@gmail.com",
    description="A library, that stores commonly used code for different modules in the CryptoOwl application",
    long_description=long_description,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pytz",
        "boto3",
        "PyMySQL",
        "redis",
        "botocore",
        "setuptools",
        "pymemcache",
        "psycopg2-binary",
        "requests",
        "pydantic"
    ],
)

from setuptools import setup, find_packages

setup(
    name="djangophone",
    version="0.1.0",
    packages=find_packages(where="core"),
    install_requires=[
        "Django>=3.2",
        "phonenumbers>=8.13",
    ],
)

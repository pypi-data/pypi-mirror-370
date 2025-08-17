from setuptools import setup, find_packages

setup(
    name="dedsec_cli",
    version="1.0",
    packages=find_packages(),
    install_requires=["pyfiglet"],
    python_requires=">=3.7",
    description="Dedsec UI helpers for Python CLIs",
    author="0xbit",
    url="https://github.com/0xbitx/dedsec_cli_utils",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)

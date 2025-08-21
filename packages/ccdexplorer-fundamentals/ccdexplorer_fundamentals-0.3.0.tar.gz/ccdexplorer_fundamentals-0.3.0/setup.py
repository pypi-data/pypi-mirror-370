from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="ccdexplorer-fundamentals",
    version="0.3.0",
    author="Sander de Ruiter",
    author_email="sdr@ccdexplorer.io",
    description="Shared code for CCDExplorer.io and its Notification Bot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccdexplorer/ccdexplorer-fundamentals",
    project_urls={},
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "python-dateutil",
        "base58",
        "eth-hash",
        "pycryptodome",
        "pytest",
        "leb128",
        "pydantic",
        "pymongo",
        "motor",
        "requests",
        "apprise",
        "py-graphql-client",
        "chardet",
        "pre-commit",
    ],
)

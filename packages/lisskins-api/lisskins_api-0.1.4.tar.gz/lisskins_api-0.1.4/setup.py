from setuptools import setup, find_packages

setup(
    name='lisskins_api',
    version='0.1.4',
    description='Module for interacting with Lis Skins API',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='$10,000 Lincoln Continental',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
    ],
)
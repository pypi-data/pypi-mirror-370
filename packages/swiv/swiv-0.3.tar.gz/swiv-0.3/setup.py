from setuptools import setup, find_packages

setup(
    name="swiv",
    version="0.3",
    packages=find_packages(),
    install_requires=["requests"],  # ensures requests is installed
    description="Dependency confusion PoC",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)

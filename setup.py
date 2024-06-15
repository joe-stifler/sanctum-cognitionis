from setuptools import setup, find_packages

setup(
    name="servitium_cognitionis",
    version="0.2.0",
    author="Joe",
    author_email="joseribeiro1017@gmail.com",
    packages=find_packages(include=['servitium_cognitionis']),
    description="A system for managing educational content and assessments in Sanctum Cognitionis.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joe/sanctum_cognitionis",
)

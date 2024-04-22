from setuptools import setup, find_packages

setup(
    name="sanctum_cognitionis",
    version="0.1.0",
    author="Joe",
    author_email="joseribeiro1017@gmail.com",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "sanctum_cognitionis=sanctum_cognitionis:main",
        ],
    },
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)

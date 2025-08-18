from setuptools import setup, find_packages

setup(
    name="opsec",
    version="0.67.41",
    author="bannisters",
    author_email="imbannisters@gmail.com",
    description="How to install opsec",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://bannisters.cc",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)

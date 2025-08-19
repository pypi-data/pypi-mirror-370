from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

setup(
    name="bg4h",
    version="1.0.23",
    author="ct.galega",
    author_email="soporte@ctgalega.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description="bg table definitions for humans",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[]
)

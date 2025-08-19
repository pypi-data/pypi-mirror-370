from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logftz",
    version="1.0.0",
    author="stdeson",
    author_email="stdeson@gmail.com",
    description="A timezone-configurable logging package based on loguru with Shanghai timezone as default",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stdeson/logftz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "loguru>=0.6.0",
        "pytz>=2021.1",
    ],
    keywords="logging loguru timezone configurable international",
)
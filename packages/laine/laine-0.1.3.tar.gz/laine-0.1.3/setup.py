from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="laine",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pillow",
        "tqdm",
        "lxml",
        "InquirerPy"
    ],
    entry_points={
        "console_scripts": [
            "laine=src.cli:main"
        ]
    },
    author="syvixor",
    description="A CLI tool to deobfuscate & download manga chapters from multiple official Japanese providers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/syvixor/laine",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console"
    ],
    python_requires=">=3.7",
    license="MIT"
)
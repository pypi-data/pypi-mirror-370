from setuptools import setup, find_packages

setup(
    name="overleaf2arxiv",
    version="0.2.2",
    packages=["overleaf2arxiv"],
    install_requires=[
        "pyoverleaf",
    ],
    entry_points={
        "console_scripts": [
            "overleaf2arxiv=overleaf2arxiv.main:main",
        ],
    },
    author="Abhay Deshpande",
    description="A tool to convert Overleaf projects to arXiv-compatible formats",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/abhayd/Overleaf2Arxiv",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
    ],
    python_requires=">=3.8",
)

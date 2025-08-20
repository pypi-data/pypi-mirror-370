from setuptools import setup, find_packages

setup(
    name="genu",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "uuid7": ["uuid6"],
    },
    entry_points={
        "console_scripts": [
            "genu=uuid_cli.cli:main",
        ]
    },
    author="Jearel Alcantara",
    author_email="jeasoft@gmail.com",
    description="A CLI tool to generate UUIDs of different versions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jeasoft/genu",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
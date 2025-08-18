from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="vsrs",
    description="Library and command line tool to rescale MSX/ViennaSweeper skins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Thomas Kolar",
    author_email="ralokt@ralokt.at",
    url="https://github.com/ralokt/vsrs/",
    packages=["vsrs"],
    entry_points={
        "console_scripts": ["vsrs=vsrs:main"],
    },
    platforms=["all"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "minesweeper",
        "vsweep",
        "viennasweeper",
        "vienna minesweeper",
    ],
    install_requires=[
        "pillow>=11.3.0",
    ],
)

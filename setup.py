#!/usr/bin/env python3

# Python imports
import os
from setuptools import setup

setup(
    name="bwcrop",
    version="0.4.0",
    author="Antti-Pekka Meronen",
    author_email="anttipekkameronen@google.com",
    description="An application to automatically crop image files.",
    url="https://github.com/bulkware/bwcrop",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Editors",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=["src"],
    entry_points={
        "console_scripts": [],
        "gui_scripts": ["bwcrop=src.bwcrop:main"]
    },
    install_requires=[
        "pillow>=8.3.1"
    ],
    python_requires=">=3.6, <4",
    project_urls={
        "Bug Reports": "https://github.com/bulkware/bwcrop/issues",
        "Source": "https://github.com/bulkware/bwcrop",
    },
)

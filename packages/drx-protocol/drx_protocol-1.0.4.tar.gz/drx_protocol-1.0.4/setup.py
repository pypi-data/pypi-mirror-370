#!/usr/bin/env python3
# encoding: utf-8
"""DrX protocol package."""
import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='drx_protocol',
      version='1.0.4',
      description='DrX protocol',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://drx.works/',
      author='DrX Works',
      author_email='info@drx.works',
      packages=find_packages(),
      package_data={"drx_protocol": ["py.typed"]},
      python_requires='>=3.10',
      install_requires=[
        'pycryptodomex',
        ],
      tests_require=[],
      platforms=['any'],
      zip_safe=False,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Science/Research",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "Programming Language :: Python :: 3.13",
          ])

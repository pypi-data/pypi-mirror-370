from io import open
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="fdsnnetextender",
    version="3.3.1",
    description="Compute extended network names from the fdsn network codes and a year using fdsn network webserice",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Jonathan Schaeffer, RESIF",
    author_email="jonathan.schaeffer@univ-grenoble-alpes.fr",
    maintainer="Jonathan Schaeffer, RESIF",
    maintainer_email="jonathan.schaeffer@univ-grenoble-alpes.fr",
    url="https://gricad-gitlab.univ-grenoble-alpes.fr/OSUG/RESIF/fdsnnetextender",
    license="GPL-3.0",
    packages=["fdsnnetextender"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    tests_require=["pytest-cov"],
)

import os
import setuptools


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        content = file.read()
    return content


setuptools.setup(
    name="evefile",
    version=read("VERSION").strip(),
    description="Transitional package to read eveH5 files containing "
    "synchrotron radiometry data recorded at BESSY/MLS in Berlin",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="till.biskup@ptb.de",
    url="https://www.ptb.de/cms/en/ptb/fachabteilungen/abt7/ptb-sr.html",
    project_urls={
        "Documentation": "https://evefile.docs.radiometry.de/",
        "Source": "https://github.com/tillbiskup/evefile",
    },
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    license="GPLv3",
    keywords=[
        "eve",
        "radiometry",
        "synchrotron",
        "PTB",
        "BESSY",
        "MLS",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "h5py",
        "numpy",
        "pandas",
    ],
    extras_require={
        "dev": [
            "prospector",
            "pyroma",
            "bandit",
            "black",
            "pymetacode",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx_multiversion",
        ],
        "deployment": [
            "build",
            "twine",
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,
)

# System imports
from setuptools import find_packages, setup

# Local imports
from SmartLeads.version import __version__ as version

# third-party imports


# Local imports should be empty otherwise there will be a cyclical dependency issue!


"""
The package build configuration file.
"""


# Setup boilerplate below this line.

entry_point = "SmartLeads = SmartLeads.__main__:main"
name = "SmartLeads"
description = "description"

# get the dependencies and installs
with open("requirements.txt", encoding="utf-8") as f:
    # Make sure we strip all comments and options (e.g "--extra-index-url")
    # that arise from a modified pip.conf file that configure global options
    # when running kedro build-reqs
    requires = []
    for line in f:
        req = line.split("#", 1)[0].strip()
        if req and not req.startswith("--"):
            requires.append(req)

setup(
    name=name,
    version=version,
    author="Anlytix Engine",
    description=description,
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": [entry_point]},
    install_requires=requires,
    extras_require={
        "docs": [
            "docutils<0.18.0",
            "sphinx~=3.4.3",
            "sphinx_rtd_theme==0.5.1",
            "nbsphinx==0.8.1",
            "nbstripout~=0.4",
            "sphinx-autodoc-typehints==1.11.1",
            "sphinx_copybutton==0.3.1",
            "ipykernel>=5.3, <7.0",
            "Jinja2<3.1.0",
            "myst-parser~=0.17.2",
        ]
    },
)

#!/usr/bin/env python3

import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
# from jtable.version import __version__
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "jtable", "version.py")
    with open(version_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                version = line.split(delim)[1]
                if version == "current":
                    return "0.0.1"
                else:
                    return version
    raise RuntimeError("Unable to find __version__ in version.py")


class CustomInstallCommand(install):
    def run(self):
        dependencies_dir = os.path.join(os.path.dirname(__file__), "dependencies")
        requirements_file = os.path.join(dependencies_dir, "requirements.txt")
        if os.path.exists(requirements_file):
            print(f"Installing dependencies from {requirements_file}")
            subprocess.check_call(["pip", "install", "--no-index", "--find-links", dependencies_dir, "-r", requirements_file])
        
        # Continuer avec l'installation normale
        install.run(self)

setup(
    name="jtable",
    version=get_version(),
    packages=find_packages(),
    # packages=find_packages(include=["jtable", "jtable.*","logger"]),
    # py_modules=["logger"],
    include_package_data=True,
    package_data={'': ['resources/*']},
    entry_points={
        'console_scripts': [
            'jtable=jtable.jtable:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,  # Utilisation de la classe personnalisée
    },
    author="Vincent Tougne",
    author_email="vtougne@gmail.com",
    description="Tabulate JSON data and transform them using Jinja templates.",
    long_description=open("doc/README_pypi.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="json, table, jinja, templating, data transformation",
    # project_urls={
    #     "Documentation": "https://jtable.readthedocs.io/en/latest/",
    #     "Source": " 
    license="MIT",
    license_files=["LICENSE.txt"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    url="https://github.com/vtougne/jtable",
    extras_require={
        "all": [
            # "beautifulsoup4",
            # "lxml",
            # "html5lib",
            # "pandas",
            # "openpyxl",
            # "xlsxwriter",
            "xmltodict",
            "html-to-json"
        ],
        "xmltodict": ["xmltodict"],
        "html-to-json": ["html-to-json"]
    },
)

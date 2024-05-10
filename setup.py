"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import os
import re
# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def get_requires(filename):
    requirements = []
    with open(filename, "rt") as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                requirements.append(line)
    return requirements


project_requirements = get_requires(os.path.join("bincrafters_conan_remote", "requirements.txt"))
# dev_requirements = get_requires(os.path.join("bincrafters_conan_remote", "requirements_dev.txt"))


setup(
    name="bincrafters-conan-remote",
    python_requires=">=3.8",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.0.1",

    description="Run locally a Conan remote that builds open static files.",
    long_description="This tool is something like a locally run proxy server to provide the Conan client with a Conan remote as it expects, building upon static remote text files.",
    long_description_content_type="text/markdown",

    url="https://github.com/bincrafters/bincrafters-conan-remote",
    project_urls={
        "Documentation": "https://github.com/bincrafters/bincrafters-conan-remote",
        "Source": "https://github.com/bincrafters/bincrafters-conan-remote",
        "Tracker": "https://github.com/bincrafters/community/issues",
    },

    author="Bincrafters",
    author_email="bincrafters@cr0ydon.com",

    license="MIT",

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],

    # What does your project relate to?
    keywords=["conan", "remote", "static", "bincrafters", "C/C++", "package", "libraries", "developer", "manager",
            "dependency", "tool", "c", "c++", "cpp"],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=project_requirements,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': dev_requirements,
    #     'test': dev_requirements,
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={
        "bincrafters_conan_remote": ["remote_repo_meta_files/*", "remote_repo_meta_files/.gitignore"],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.8/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'conan=conans.conan:run',
    #        'conan_server=conans.conan_server:run',
    #        'conan_build_info=conans.build_info.command:run'
    #    ],
    #},
)

#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "5.12.4"

setuptools.setup(
    name='ccfit2',
    version=__version__,
    description='CCFIT2 is a program for fitting AC and DC magnetisation data', # noqa
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/chilton-group/cc-fit2",
    project_urls={
        "Bug Tracker": "https://gitlab.com/chilton-group/cc-fit2/-/issues",
        "Documentation": "https://chilton-group.gitlab.io/cc-fit2"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10',
    install_requires=[
        'numpy>=2.1.0',
        'scipy>=1.14.1',
        'matplotlib>=3.9.2',
        'pillow>=10.4.0',
        'qtpy>=2.4.1',
        'pyqtgraph>=0.13.7',
        'charset_normalizer>=3.3.2',
        'pandas>=2.2.2'
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'ccfit2 = ccfit2.cli:main',
            'cc_fit2 = ccfit2.cli:main',
            'cc-fit2 = ccfit2.cli:main',
            'update_ac_dc_params = ccfit2.scripts.update_ac_dc_params:main',
            'split_rates = ccfit2.scripts.split_rates:main'
        ]
    }
)

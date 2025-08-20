#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['teradataml>=20.0.00.00',
                'scikit-learn>=1.2.0',
                'numpy>=1.24.2',
                'sqlparse'
                ]

extras_require = {
    'plot': ["plotly>=5.0", "seaborn>=0.11", "networkx","sqlparse"]
}


setup(
    name='teradataml-plus', # PyPI name
    version='0.3.1',
    description="Python Package that extends the functionality of the popular teradataml package through monkey-patching.",

    author="Martin Hillebrand",
    author_email='martin.hillebrand@teradata.com',

    packages=find_packages(include=['tdmlplus', 'tdmlplus.*']), # # actual importable module

    python_requires='>=3.9',
    install_requires=requirements,
    extras_require=extras_require,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
    ],
    keywords='teradataml-plus,teradata,database,teradataml',

    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,

    zip_safe=False,
)



#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Sergi Novellas",
    author_email='sernocr@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Module for backtesting algorithmic trading strategies",
    entry_points={
        'console_scripts': [
            'alphabacktest=alphabacktest.cli:main',
        ],
    },
    install_requires=['Click>=7.0', 'progressbar2>=3.53.1','pandas>=1.1.4','pandas_datareader>=0.9.0'],
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='alphabacktest',
    name='alphabacktest',
    packages=find_packages(include=['alphabacktest', 'alphabacktest.*','_dash_results.*']),
    package_data={'assets':['*'] },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/serginc21/alphabacktest',
    version='0.1.5',
    zip_safe=False,
)

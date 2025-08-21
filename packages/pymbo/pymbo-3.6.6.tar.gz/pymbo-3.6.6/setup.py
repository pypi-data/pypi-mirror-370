#!/usr/bin/env python3
"""
Setup script for PyMBO - Python Multi-objective Bayesian Optimization
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
version_info = {}
with open(os.path.join('pymbo', '__init__.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version_info)
        elif line.startswith('__author__'):
            exec(line, version_info)

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymbo',
    version=version_info['__version__'],
    author=version_info['__author__'],
    author_email='jakubjagielski93@gmail.com',
    description='Python Multi-objective Bayesian Optimization framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/pymbo/',
    project_urls={
        'Bug Reports': 'https://github.com/jakub-jagielski/pymbo/issues',
        'Source': 'https://github.com/jakub-jagielski/pymbo',
        'Documentation': 'https://github.com/jakub-jagielski/pymbo#readme',
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pymbo=pymbo.launcher:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
    ],
    keywords='bayesian-optimization multi-objective optimization machine-learning',
    license='MIT',
)
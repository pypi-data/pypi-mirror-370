#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

# Read version from __init__.py
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'adsonai_sdk', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip().strip('"\'')
            break

# Read the contents of README file
with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(here, 'requirements.txt'), 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='adsonai',
    version=version,
    description='Python SDK for AdsonAI contextual advertising platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AdsonAI Team',
    author_email='support@adsonai.com',
    url='https://github.com/adsonai/adsonai-python-sdk',
    project_urls={
        'Documentation': 'https://docs.adsonai.com',
        'Source': 'https://github.com/adsonai/adsonai-python-sdk',
        'Tracker': 'https://github.com/adsonai/adsonai-python-sdk/issues',
    },
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.14.0',
            'pytest-mock>=3.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'pre-commit>=2.0',
        ],
        'docs': [
            'sphinx>=3.0',
            'sphinx-rtd-theme>=0.5',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial',
    ],
    keywords='advertising ai llm contextual ads monetization',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)
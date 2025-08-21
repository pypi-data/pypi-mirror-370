#!/usr/bin/env python
"""Setup script for vector_store_client package."""

from setuptools import setup, find_packages
import os
import re

# Read version from the package
version = "2.0.0.3"
try:
    with open(os.path.join('vector_store_client', '__init__.py'), 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                version = re.match(r"__version__\s*=\s*'(.*)'", line).group(1)
                break
except:
    pass

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vector_store_client',
    version=version,
    description='Client for interacting with Vector Store API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Vasily Zdanovskiy',
    author_email='vasilyvz@gmail.com',
    url='https://github.com/vector-store/vector_store_client',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.8',
    install_requires=[
        'httpx>=0.24.0',
        'pydantic>=2.0.0',
        'jsonschema>=4.0.0',
        'typing-extensions>=4.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.18.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'mypy>=0.910',
            'ruff>=0.0.100',
        ],
    },
    keywords='vector, embeddings, vector-database, semantic-search, api-client',
    project_urls={
        'Documentation': 'https://github.com/vector-store/vector_store_client/tree/main/docs',
        'Source': 'https://github.com/vector-store/vector_store_client',
        'Tracker': 'https://github.com/vector-store/vector_store_client/issues',
    },
) 
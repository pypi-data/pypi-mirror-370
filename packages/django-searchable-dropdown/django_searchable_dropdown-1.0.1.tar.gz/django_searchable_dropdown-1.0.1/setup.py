#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script para SearchableDropdown
"""

import os
import re
from setuptools import setup, find_packages

# Função para ler o README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Função para obter a versão do __init__.py
def get_version():
    with open('recoveredperispirit/django/django_searchable_dropdown/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Não foi possível encontrar a versão.")

# Função para obter os requisitos
def get_requirements():
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return requirements

setup(
    name='django_searchable_dropdown',
    version=get_version(),
    description='Biblioteca Django para criar dropdowns pesquisáveis e customizáveis',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Marcio Bernardes',
    author_email='marciobernardes@live.com',
    url='https://github.com/novaalvorada/django_searchable_dropdown',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
    keywords='django dropdown searchable select widget form field',
    install_requires=get_requirements(),
    python_requires='>=3.7',
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-django>=4.0',
            'black>=22.0',
            'flake8>=4.0',
            'isort>=5.0',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/novaalvorada/django_searchable_dropdown/issues',
        'Source': 'https://github.com/novaalvorada/django_searchable_dropdown',
        'Documentation': 'https://django_searchable_dropdown.readthedocs.io/',
    },
)

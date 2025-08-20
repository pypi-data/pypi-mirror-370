# setup.py
# -*- coding: utf-8 -*-
#
#o mejor aun correr en BASH :
#
#            sh update.sh
#
#para instalar usar:
#
#pip3 install libPy2023 --upgrade
#
#El Proyecto esta en
#        https://pypi.org/manage/projects/
#        https://github.com/Dexsys
#
#

import setuptools
import re




def get_version():
    with open("libPy2023/__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("No version found in __init__.py")

with open('README.md','r',encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='libPy2023',
    version=get_version(),
    author='Ludwig R. Corales Marti',
    author_email='dexsys@gmail.com',
    description='Librerías de propósito General',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Dexsys/libPy2023',
    #packages=setuptools.find_packages(exclude=['sphinx_docs', 'docs', 'tests']),
    python_requires='~=3.5',
    install_requires=[
        "keyboard",
        "pandas",
        "pywin32",
        "setuptools"
    ],
    extras_require={
        'dev': ['setuptools', 'wheel', 'twine', 'Sphinx'],
    },
    license='Proprietary; Free for non-commercial use',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development',
        'Operating System :: OS Independent',
        'Natural Language :: Spanish'
    ],
)
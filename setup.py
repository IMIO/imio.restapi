# -*- coding: utf-8 -*-
"""Installer for the imio.restapi package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='imio.restapi',
    version='1.0a2',
    description="Extended rest api service for IMIO usecases",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Martin Peeters',
    author_email='martin.peeters@affinitic.be',
    url='https://pypi.python.org/pypi/imio.restapi',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'setuptools',
        'z3c.jbot',
        'plone.restapi',
        'collective.z3cform.select2',
    ],
    extras_require={
        'test': [
            'collective.documentgenerator',
            'plone.app.robotframework[debug]',
            'plone.restapi[test]',
            'Products.ATContentTypes',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = imio.restapi.locales.update:update_locale
    """,
)

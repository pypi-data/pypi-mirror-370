#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='ebas-io',
      version='4.04.01',
      description='EBAS file I/O',
      author='Paul Eckhardt, NILU',
      author_email='pe@nilu.no',
      license='agpl 3.0',
      #url='https://www.python.org/sigs/distutils-sig/',
      packages=find_packages(exclude=["*.test", "*.test.*"]),                    

      # add pkl files for offline masterdata:
      include_package_data=True,
      package_data={'ebas.domain.masterdata.offline_masterdata': ['*.pkl']},
      install_requires=['python-dateutil', 'datadiff'],
     )


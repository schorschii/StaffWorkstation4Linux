from distutils.command.clean import clean
from distutils import log
from setuptools import setup
import os

setup(
      name='bookchecker',
      description='"3M Staff Workstation" software for Linux, which controls the 3M Bookcheck Unit Model 940 Series',
      install_requires=[i.strip() for i in open('requirements.txt').readlines()],
      author='Georg Sieber',
      packages=['bookchecker'],
      entry_points={
            'console_scripts': [
                  'bookchecker = bookchecker.bookchecker:main',
            ],
      },
      platforms=['all'],
      #install_requires=[],
      #test_suite='tests',
)

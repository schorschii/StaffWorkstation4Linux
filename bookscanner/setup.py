from distutils.command.clean import clean
from distutils import log
from setuptools import setup
import os

setup(
      name='bookscanner',
      description='"3M Staff Workstation" software for Linux, which controls the Microscan MS-820 Scanner over serial port',
      install_requires=[i.strip() for i in open('requirements.txt').readlines()],
      author='Georg Sieber',
      packages=['bookscanner'],
      entry_points={
            'console_scripts': [
                  'bookscanner = bookscanner.bookscanner:main',
            ],
      },
      platforms=['all'],
      #install_requires=[],
      #test_suite='tests',
)

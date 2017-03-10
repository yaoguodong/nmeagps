# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='nmeagps',
    version='0.1.0',
    description='Randomized NMEA-1083 GPS message generator.',
    long_description=readme,
    author='Jonathan Racicot',
    author_email='cyberrecce@gmail.com',
    url='https://github.com/infectedpacket/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)


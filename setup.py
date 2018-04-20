import os
import sys

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "src")

sys.path.insert(0, src_dir)

setup(
    name='Zabbix Tool',
    install_requires=['pyzabbix', 'mongoengine'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock', 'mongomock'],
    packages=find_packages(),
    include_package_data=True,
)

dependency_links=['https://artifactory.globoi.com/artifactory/api/pypi/pypi-all/simple/']

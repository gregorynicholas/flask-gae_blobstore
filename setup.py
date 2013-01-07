#!/usr/bin/env python
"""
flask-gae_blobstore
-----------------------

Flask extension for working with the blobstore & files apis on
App Engine.

Links
`````

* `documentation <http://packages.python.org/flask-gae_blobstore>`_
* `development version
  <http://github.com/gregorynicholas/flask-gae_blobstore/zipball/master#egg=flask_gae_blobstore-dev>`_

"""
from setuptools import setup

setup(
  name='flask-gae_blobstore',
  version='1.0.0',
  url='http://github.com/gregorynicholas/flask-gae_blobstore',
  license='MIT',
  author='gregorynicholas',
  description='Flask extension module for working with the blobstore & files \
apis on App Engine.',
  long_description=__doc__,
  py_modules=['flask_gae_blobstore'],
  # packages=['flaskext'],
  # namespace_packages=['flaskext'],
  include_package_data=True,
  data_files=['test.jpg'],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'flask',
  ],
  tests_require=[
    'nose',
    'flask_gae_tests',
  ],
  dependency_links = [
    'https://github.com/gregorynicholas/flask-gae_tests/tarball/master',
  ],
  test_suite='nose.collector',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)

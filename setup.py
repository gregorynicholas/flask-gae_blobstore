#!/usr/bin/env python
"""
flask-gae_blobstore
~~~~~~~~~~~~~~~~~~~

flask extension for working with the blobstore & files apis on
app engine.


links
`````

* `docs <http://gregorynicholas.github.io/flask-gae_blobstore>`_
* `source <http://github.com/gregorynicholas/flask-gae_blobstore>`_
* `package <http://packages.python.org/flask-gae_blobstore>`_
* `travis-ci <http://travis-ci.org/gregorynicholas/flask-gae_blobstore>`_

"""
from setuptools import setup

__version__ = "1.0.2"

with open("requirements.txt", "r") as f:
  requires = f.readlines()

with open("README.md", "r") as f:
  long_description = f.readlines()


setup(
  name='flask-gae_blobstore',
  version=__version__,
  url='http://github.com/gregorynicholas/flask-gae_blobstore',
  license='MIT',
  author='gregorynicholas',
  author_email='gn@gregorynicholas.com',
  description=__doc__,
  long_description=long_description,
  py_modules=[
    'flask_gae_blobstore',
    'flask_gae_blobstore_tests',
  ],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'flask==2.3.2',
  ],
  tests_require=[
    'flask-funktional-gae==0.0.1',
  ],
  dependency_links=[
  ],
  test_suite='flask_gae_blobstore_tests',
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

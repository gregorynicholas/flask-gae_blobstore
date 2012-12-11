"""
Flask App Engine Blobstore
-----------------------

Flask extension module for working with the blobstore & files api on App Engine.

Links
`````

* `documentation <http://packages.python.org/Flask%20App%20Engine%20Blobstore>`_
* `development version
  <http://github.com/gregorynicholas/flask-gae_blobstore/zipball/master#egg=flask_gae_blobstore-dev>`_

"""
from setuptools import setup


setup(
  name='Flask App Engine Blobstore',
  version='1.0.0',
  url='http://github.com/gregorynicholas/flask-gae_blobstore',
  license='BSD',
  author='gregorynicholas',
  description='Flask extension module for working with the blobstore & files api on App Engine.',
  long_description=__doc__,
  py_modules=['gae_blobstore'],
  # packages=['flaskext'],
  # namespace_packages=['flaskext'],
  include_package_data=True,
  data_files=[('', ['test_file.jpg'])],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'Flask'
  ],
  test_suite='gae_blobstore_tests',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)

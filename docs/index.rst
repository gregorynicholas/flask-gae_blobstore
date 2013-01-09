Flask App Engine Blobstore
==========================

`Flask`_ extension for working with the blobstore & files api on `App Engine`_.

Links
-----

* :ref:`genindex`
* `documentation <http://packages.python.org/flask-gae_blobstore/>`_
* `source <http://github.com/gregorynicholas/flask-gae_blobstore>`_
* :doc:`changelog </changelog>`

Installing flask-gae_blobstore
------------------------------

Install with **pip**

    `pip install https://github.com/gregorynicholas/flask-gae_blobstore/tarball/master`




API
---

.. module:: flask_gae_blobstore

.. members: WRITE_SLEEP_SECONDS, WRITE_MAX_RETRIES, DEFAULT_NAME_LEN, MSG_INVALID_FILE_POSTED, UPLOAD_MIN_FILE_SIZE, UPLOAD_MAX_FILE_SIZE, UPLOAD_ACCEPT_FILE_TYPES, ORIGINS, OPTIONS, HEADERS, MIMETYPE

.. autoclass:: RemoteResponse

  .. automethod:: __init__

.. autoclass:: FieldResultSet

  .. automethod:: __init__
  .. automethod:: to_dict

.. autoclass:: FieldResult

  .. automethod:: __init__
  .. automethod:: to_dict

.. autofunction:: upload_blobs

.. autofunction:: validate

.. autofunction:: save_blobs

.. autofunction:: get_field_size

.. autofunction:: write_to_blobstore




----

.. _Flask: http://flask.pocoo.org
.. _App Engine: http://appengine.google.com

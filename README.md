flask-gae_blobstore
===================

[flask](http://flask.pocoo.org) extension to make working with the `blobstore`
and `files` apis on [google app-engine](http://appengine.google.com) more enjoyable


<br>
**build-status:**

`master ` [![travis-ci build-status: master](https://secure.travis-ci.org/gregorynicholas/flask-gae_blobstore.svg?branch=master)](https://travis-ci.org/gregorynicholas/flask-gae_blobstore)
<br>
`develop` [![travis-ci build-status: develop](https://secure.travis-ci.org/gregorynicholas/flask-gae_blobstore.svg?branch=develop)](https://travis-ci.org/gregorynicholas/flask-gae_blobstore)


**links:**

* [homepage](http://gregorynicholas.github.io/flask-gae_blobstore)
* [source](http://github.com/gregorynicholas/flask-gae_blobstore)
* [python-package](http://packages.python.org/flask-gae_blobstore)
* [github-issues](https://github.com/gregorynicholas/flask-gae_blobstore/issues)
* [changelog](https://github.com/gregorynicholas/flask-gae_blobstore/blob/master/CHANGES.md)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-gae_blobstore)


<br>
-----
<br>


### getting started


install with pip:

    $ pip install flask-gae_blobstore


<br>
-----
<br>


### features

* [todo]


<br>
-----
<br>


### example usage

    from flask.ext import gae_blobstore
    from flask import json
    from flask import Flask
    from google.appengine.ext import ndb

    class TestModel(ndb.Model):
      blob_key = ndb.BlobKeyProperty()

    app = Flask(__name__)

    @app.route('/test_upload', methods=['POST'])
    @gae_blobstore.upload_blobs()
    def test_upload(blobs):
      try:
        entities = []
        for blob in blobs:
          entity = TestModel(
            blob_key=blob.blob_key)
          entities.append(entity)
        ndb.put_multi(entities)
      except:
        # rollback the operation and delete the blobs,
        # so they are not orphaned..
        for blob in blobs:
          gae_blobstore.delete(blob.blob_key)
        raise Exception('Saving file upload info to datastore failed..')
      return json.dumps(blobs.to_dict())

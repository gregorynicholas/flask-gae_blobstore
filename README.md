flask-gae_blobstore
===================

flask extension for working with the blobstore & files apis on
app engine.


[![Build Status](https://secure.travis-ci.org/gregorynicholas/flask-gae_blobstore.png?branch=master)](https://travis-ci.org/gregorynicholas/flask-gae_blobstore)


* [docs](http://gregorynicholas.github.io/flask-gae_blobstore)
* [source](http://github.com/gregorynicholas/flask-gae_blobstore)
* [package](https://pypi.python.org/pypi/flask-gae_blobstore)
* [changelog](https://github.com/gregorynicholas/flask-gae_blobstore/blob/master/CHANGES.md)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-gae_blobstore)


----


### getting started

install with *pip*:

    pip install flask-gae_blobstore


-----


### overview

* [todo]


### features

* [todo]


-----


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

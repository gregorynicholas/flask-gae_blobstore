# flask-gae_blobstore

--------------

Flask extension for working with the blobstore & files api on App Engine.

[![Build Status](https://secure.travis-ci.org/gregorynicholas/flask-gae_blobstore.png?branch=master)](https://travis-ci.org/gregorynicholas/flask-gae_blobstore)

----

### install with pip
`pip install https://github.com/gregorynicholas/flask-gae_blobstore/tarball/master`

### usage

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



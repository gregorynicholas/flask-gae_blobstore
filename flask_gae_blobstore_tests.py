#!/usr/bin/env python
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

import unittest
from flask import json
from flask import Flask
from flask.ext import gae_tests
from flask.ext import gae_blobstore
from google.appengine.api import files
from google.appengine.ext import ndb


# test application..

class TestModel(ndb.Model):
  blob_key = ndb.BlobKeyProperty()

app = Flask(__name__)
app.debug = True
app.request_class = gae_tests.FileUploadRequest

@app.route('/test_upload', methods=['POST', 'OPTIONS', 'HEAD', 'PUT'])
@gae_blobstore.upload_blobs()
def test_upload(blobs):
  entities = []
  try:
    for blob in blobs:
      entity = TestModel(
        blob_key=blob.blob_key)
      entities.append(entity)
    ndb.put_multi(entities)
  except:
    # rollback the operation and delete the blobs,
    # so they are not orphaned..
    for blob in blobs:
      blob.delete()
    raise Exception('Saving file upload info to datastore failed..')
  return json.dumps(blobs.to_dict())


# test cases..

class TestCase(gae_tests.TestCase):

  def test_blobstore_sanity_check(self):
    filename = files.blobstore.create(mime_type='application/octet-stream')
    self.assertNotEquals(None, filename)
    with files.open(filename, 'a') as f:
      f.write('test blob data..')
    files.finalize(filename)
    blobkey = files.blobstore.get_blob_key(filename)
    self.assertNotEquals(None, blobkey)

  def test_upload_returns_valid_blob_result(self):
    data, filename, size = gae_tests.open_test_file('test.jpg')
    response = app.test_client().post(
      data={'test': (data, filename)},
      path='/test_upload',
      headers={},
      query_string={})
    self.assertEqual(200, response.status_code)
    result = json.loads(response.data)
    self.assertIsInstance(result, list)
    self.assertEquals(1, len(result))
    self.assertEquals(True, result[0].get('successful'))
    # check the file name is the same..
    self.assertEquals(filename, result[0].get('name'))
    # check file size is the same..
    self.assertEquals(size, result[0].get('size'))
    # validate the blob_key..
    self.assertTrue(len(result[0].get('blob_key')) > 0)


if __name__ == '__main__':
  unittest.main()

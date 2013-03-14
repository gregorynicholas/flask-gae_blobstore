#!/usr/bin/env python
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

import unittest, logging
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
def test_upload(uploads):
  entities = []
  try:
    for upload in uploads:
      entity = TestModel(
        blob_key=upload.blob_key)
      entities.append(entity)
      blob_info = upload.blob_info
      logging.info('upload.blob_info: %s', blob_info)
    ndb.put_multi(entities)
  except:
    # rollback the operation and delete the blobs,
    # so they are not orphaned..
    for upload in uploads:
      gae_blobstore.delete(upload.blob_key)
    raise Exception('Saving file upload info to datastore failed..')
  return json.dumps(uploads.to_dict())


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

  def _assertUploadResult(self, result, filename, size):
    self.assertEquals(True, result['successful'])
    # check the file name is the same..
    self.assertEquals(filename, result['name'])
    # check file size is the same..
    self.assertEquals(size, result['size'])
    # validate the blob_key..
    self.assertTrue(len(result['blob_key']) > 0)
    blob_key = gae_blobstore.BlobKey(result['blob_key'])
    blob_info = gae_blobstore.blobstore.get(blob_key)
    self.assertEquals(blob_info.filename, filename)
    self.assertEquals(blob_info.size, size)

  def test_upload_returns_valid_blob_result(self):
    data, filename, size = gae_tests.create_test_file('test.jpg')
    response = app.test_client().post(
      data={'test': (data, filename)},
      path='/test_upload',
      headers={},
      query_string={})
    self.assertEqual(200, response.status_code)
    results = json.loads(response.data)
    self.assertIsInstance(results, list)
    self.assertEquals(1, len(results), results)
    self._assertUploadResult(results[0], filename, size)

  def test_multiple_uploads_return_all_results(self):
    testfiles = [gae_tests.create_test_file('test%d.jpg' % x) for x in range(5)]
    tests = {x[0]: (x[0], x[1]) for x in testfiles}
    response = app.test_client().post(
      data=tests,
      path='/test_upload',
      headers={},
      query_string={})
    self.assertEqual(200, response.status_code)
    results = json.loads(response.data)
    self.assertIsInstance(results, list)
    self.assertEquals(len(testfiles), len(results), results)
    for testfile, result in zip(testfiles, results):
        filename = testfile[1]
        size = testfile[2]
        self._assertUploadResult(result, filename, size)

  def test_empty_upload_post_returns_empty_list(self):
    response = app.test_client().post(
      data={'test': ''},
      path='/test_upload',
      headers={},
      query_string={})
    self.assertEqual(200, response.status_code)
    results = json.loads(response.data)
    self.assertIsInstance(results, list)
    self.assertEquals(0, len(results), results)


if __name__ == '__main__':
  unittest.main()

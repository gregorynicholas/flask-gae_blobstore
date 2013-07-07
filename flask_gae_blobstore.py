"""
  flask_gae_blobstore
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for working with the blobstore & files apis on
  App Engine.

  :copyright: (c) 2013 by gregorynicholas.
  :license: BSD, see LICENSE for more details.
"""
import re
import time
# Uses of a deprecated module 'string'
# pylint: disable-msg=W0402
import string
import random
import logging
from flask import request, make_response
from functools import wraps
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobKey


__all__ = [
  # uploading..
  'upload_blobs', 'BlobUploadResultList', 'BlobUploadResult', "UploadConfig",
  # downloading + serving..
  "init_app", "serve_blob", "send_blob_download",
  # proxied objects..
  'delete', 'delete_async', 'fetch_data', 'fetch_data_async', 'BlobKey',
]

# proxy gae blobstore objects..
delete = blobstore.delete
delete_async = blobstore.delete_async
fetch_data = blobstore.fetch_data
fetch_data_async = blobstore.fetch_data_async


class UploadConfig(object):
  """
  configuration options for uploading to the blobstore.
  """

#:
WRITE_MAX_RETRIES = 3
#:
WRITE_SLEEP_SECONDS = 0.05
#:
DEFAULT_NAME_LEN = 20
#:
MSG_INVALID_FILE_POSTED = 'Invalid file posted.'
#:
UPLOAD_MIN_FILE_SIZE = 1
#:
UPLOAD_MAX_FILE_SIZE = 1024*1024
# set by default to images..
#:
UPLOAD_ACCEPT_FILE_TYPES = re.compile('image/(gif|p?jpeg|jpg|(x-)?png|tiff)')


class BlobUploadResultList(list):
  def to_dict(self):
    """
      :returns: list of `BlobUploadResult` as `dict`s
    """
    result = []
    for field in self:
      result.append(field.to_dict())
    return result


class BlobUploadResult(object):
  """
    :param successful:
    :param error_msg:
    :param blob_key:
    :param name:
    :param type:
    :param size:
    :param field:
    :param value:
  """
  def __init__(self, name, type, size, field, value):
    self.successful = False
    self.error_msg = ''
    self.blob_key = None
    self.name = name
    self.type = type
    self.size = size
    self.field = field
    self.value = value

  @property
  def blob_info(self):
    return blobstore.get(self.blob_key)

  def to_dict(self):
    """
      :returns: Instance of a dict.
    """
    return {
      'successful': self.successful,
      'error_msg': self.error_msg,
      'blob_key': str(self.blob_key),
      'name': self.name,
      'type': self.type,
      'size': self.size,
      # these two are commented out so the class is easily json serializable..
      # 'field': self.field,
      # 'value': self.value,
    }


def upload_blobs(validators=None):
  """
  flask route handler decorator for writing posted files to the `blobstore`
  using the app engine files api.  passes an argument to the method with a list
  of `BlobUploadResult` with `BlobKey`, name, type, size for each posted input
  file.

    :param validators: list of callable objects
  """
  def wrapper(fn):
    @wraps(fn)
    def decorated(*args, **kw):
      return fn(uploads=save_blobs(
        fields=_upload_fields(), validators=validators), *args, **kw)
    return decorated
  return wrapper


def save_blobs(fields, validators=None):
  """
  returns a list of `BlobUploadResult` with BlobKey, name, type, size for
  each posted file.

    :param fields: list of `cgi.FieldStorage` objects
    :param validators: list of callable objects
    :returns: instance of a `BlobUploadResultList`
  """
  if validators is None:
    validators = [
      validate_min_size,
      # validate_file_type,
      # validate_max_size,
    ]
  results = BlobUploadResultList()
  i = 0
  for name, field in fields:
    value = field.stream.read()
    result = BlobUploadResult(
      name=re.sub(r'^.*\\', '', field.filename.decode('utf-8')),
      type=field.mimetype,
      size=len(value),
      field=field,
      value=value)
    if validators:
      for fn in validators:
        if not fn(result):
          result.successful = False
          result.error_msg = MSG_INVALID_FILE_POSTED
          logging.warn('Error in file upload: %s', result.error_msg)
        else:
          result.blob_key = write_to_blobstore(
            result.value, mime_type=result.type, name=result.name)
          if result.blob_key:
            result.successful = True
          else:
            result.successful = False
      results.append(result)
    else:
      result.blob_key = write_to_blobstore(
        result.value, mime_type=result.type, name=result.name)
      logging.error('result.blob_key: %s', result.blob_key)
      if result.blob_key:
        result.successful = True
      else:
        result.successful = False
      results.append(result)
    i += 1
  return results


def _upload_fields():
  """
    :returns: list of tuples of filename, `FieldStorage` pairs
  """
  result = []
  for key, value in request.files.iteritems():
    if type(value) is not unicode:
      result.append((key, value))
  return result


def get_field_size(field):
  """
    :param field: instance of `FieldStorage`
    :returns: integer
  """
  try:
    field.seek(0, 2)  # seek to the end of the file
    size = field.tell()  # get the position of EOF
    field.seek(0)  # reset the file position to the beginning
    return size
  except:
    return 0


def validate_max_size(result, max_file_size=UPLOAD_MAX_FILE_SIZE):
  """
  validates an upload input based on maximum size.

    :param result: instance of `BlobUploadResult`
    :param max_file_size: integer of the maximum file size
    :returns: boolean, True if field validates
  """
  if result.size > max_file_size:
    result.error_msg = 'max_file_size'
    return False
  return True


def validate_min_size(result, min_file_size=UPLOAD_MIN_FILE_SIZE):
  """
  validates an upload input based on minimum size.

    :param result: instance of `BlobUploadResult`
    :param min_file_size: integer of the minimum file size
    :returns: boolean, True if field validates
  """
  if result.size < min_file_size:
    result.error_msg = 'min_file_size'
    return False
  return True


def validate_file_type(result, accept_file_types=UPLOAD_ACCEPT_FILE_TYPES):
  """
  validates an upload input based on accepted mime types. if validation fails,
  sets an error property to the field arg dict.

    :param result: instance of `BlobUploadResult`
    :param accept_file_types: instance of a regex
    :returns: boolean, True if field validates
  """
  # only allow images to be posted to this handler
  if not accept_file_types.match(result.type):
    result.field.error_msg = 'accept_file_types'
    return False
  return True


def write_to_blobstore(data, mime_type, name=None):
  """
  writes data (file) to the app engine blobstore and returns an instance of a
  `BlobKey` if successful.

    :param data: blob contents stream
    :param mime_type: string mime type of the blob
    :param name: string name of the blob
    :returns: instance of a `BlobKey`
  """
  random_name = lambda: "".join(
    random.choice(string.letters) for _ in range(DEFAULT_NAME_LEN))
  name = name or random_name()
  try:
    blob = files.blobstore.create(
      mime_type=mime_type,
      _blobinfo_uploaded_filename=name)
    with files.open(blob, 'a', exclusive_lock=True) as f:
      f.write(data)
    files.finalize(blob)
    result = files.blobstore.get_blob_key(blob)
    # issue with the local development SDK. we can only write to the blobstore
    # so fast, so set a retry_count and delay the execution thread between
    # each attempt..
    for i in range(1, WRITE_MAX_RETRIES):
      if result:
        break
      else:
        logging.debug('blob still None.. will retry to write to blobstore..')
        time.sleep(WRITE_SLEEP_SECONDS)
        result = files.blobstore.get_blob_key(blob)
      logging.debug('File written to blobstore: key: "%s"', result)
    return result
  except:
    import traceback
    logging.exception(
      "exception writing to the blobstore: %s", traceback.format_exc())


def _send_blob(data, filename, content_type, blob_key=None):
  """
    :param data: stream data that will be sent as the file contents
    :param filename: string name of the file
    :param content_type: string content-type of the file
    :returns: instance of a `flask.Response`
  """
  headers = {
    b'Content-Type': content_type,
    b'Content-Encoding': content_type,
    b'Content-Disposition': b'attachment; filename={}'.format(filename)}
  if blob_key:
    headers[blobstore.BLOB_KEY_HEADER] = blob_key
  return make_response((data, 200, headers))


def send_blob_download():
  """
  flask route handler decorator which sends a file to a client for downloading.

    :param data: stream data that will be sent as the file contents
    :param filename: string name of the file
    :param content_type: string content-type of the file
  """
  def wrapper(fn):
    @wraps(fn)
    def decorated(*args, **kw):
      data, filename, content_type, blob_key = fn(*args, **kw)
      return _send_blob(data, filename, content_type, blob_key)
    return decorated
  return wrapper


def serve_blob(blob_key):
  """
    :param bob_key:
    :returns: instance of a `flask.Response`
  """
  binfo = blobstore.get(blob_key)
  if not binfo:
    return None
  return _send_blob("", binfo.filename, binfo.content_type, blob_key)


def init_app(flaskapp, url, **route_kwargs):
  """
  initialized a Flask app by adding a default route for serving blobs by url.
  """
  url = url = "/blob/<blob_key>"

  @flaskapp.route(url, **route_kwargs)
  def get_blob(blob_key):
    page_not_found = lambda: ValueError("page not found")
    return serve_blob(blob_key) or page_not_found()

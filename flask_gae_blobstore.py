"""
  flask_gae_blobstore
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for working with the blobstore & files apis on
  App Engine.

  :copyright: (c) 2012 by gregorynicholas.
  :license: BSD, see LICENSE for more details.
"""
import re
import time
# Uses of a deprecated module 'string'
# pylint: disable-msg=W0402
import string
import random
import logging
from flask import Response, request
from werkzeug import exceptions
from functools import wraps
from google.appengine.api import files
from google.appengine.ext import blobstore

__all__ = ['delete', 'delete_async', 'fetch_data', 'fetch_data_async',
'WRITE_MAX_RETRIES', 'WRITE_SLEEP_SECONDS', 'DEFAULT_NAME_LEN',
'MSG_INVALID_FILE_POSTED', 'UPLOAD_MIN_FILE_SIZE', 'UPLOAD_MAX_FILE_SIZE',
'UPLOAD_ACCEPT_FILE_TYPES', 'ORIGINS', 'OPTIONS', 'HEADERS', 'MIMETYPE',
'RemoteResponse', 'FieldResultSet', 'FieldResult', 'upload_blobs',
'save_blobs', 'write_to_blobstore']

delete = blobstore.delete
delete_async = blobstore.delete_async
fetch_data = blobstore.fetch_data
fetch_data_async = blobstore.fetch_data_async

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

# todo: need a way to easily configure these values..
#:
ORIGINS = '*'
#:
OPTIONS = ['OPTIONS', 'HEAD', 'GET', 'POST', 'PUT']
#:
HEADERS = ['Accept', 'Content-Type', 'Origin', 'X-Requested-With']
#:
MIMETYPE = 'application/json'

class RemoteResponse(Response):
  '''Base class for remote service `Response` objects.

    :param response:
    :param mimetype:
  '''
  default_mimetype = MIMETYPE
  def __init__(self, response=None, mimetype=None, *args, **kw):
    if mimetype is None:
      mimetype = self.default_mimetype
    Response.__init__(self, response=response, mimetype=mimetype, **kw)
    self._fixcors()

  def _fixcors(self):
    self.headers['Access-Control-Allow-Origin'] = ORIGINS
    self.headers['Access-Control-Allow-Methods'] = ', '.join(OPTIONS)
    self.headers['Access-Control-Allow-Headers'] = ', '.join(HEADERS)

class FieldResultSet(list):
  def to_dict(self):
    '''
      :returns:
    '''
    result = []
    for field in self:
      result.append(field.to_dict())
    return result

class FieldResult:
  '''
    :param successful:
    :param error_msg:
    :param blob_key:
    :param name:
    :param type:
    :param size:
    :param field:
    :param value:
  '''
  def __init__(self, name, type, size, field, value):
    self.successful = False
    self.error_msg = ''
    self.blob_key = None
    self.name = name
    self.type = type
    self.size = size
    self.field = field
    self.value = value

  def to_dict(self):
    '''
      :returns:
    '''
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

def upload_blobs(validations=None):
  '''Method decorator for writing posted files to the `blobstore` using the
  App Engine files api. Passes an argument to the method with a list of
  `FieldResult` with `BlobKey`, name, type, size for each posted input file.

    :param validations:
  '''
  def wrapper(func):
    @wraps(func)
    def decorated(*args, **kw):
      return func(blobs=save_blobs(
        fields=_upload_fields(), validations=validations), *args, **kw)
    return decorated
  return wrapper

def save_blobs(fields, validations=None):
  '''Returns a list of `FieldResult` with BlobKey, name, type, size for
  each posted file.

    :param fields:
    :param validations:

    :returns:
  '''
  results = FieldResultSet()
  i = 0
  # validate_file_type=False,
  # validate_min_file_size=False,
  # validate_max_file_size=False
  for name, field in fields:
    value = field.stream.read()
    result = FieldResult(
      name=re.sub(r'^.*\\', '', field.filename),
      type=field.content_type,
      size=len(value),
      field=field,
      value=value)
    if not validate(result):
      result.successful = False
      result.error_msg = MSG_INVALID_FILE_POSTED
      logging.warn('Error in file upload: %s', result.error_msg)
    else:
      result.blob_key = write_to_blobstore(
        result.value, result.type, result.name)
      if result.blob_key:
        result.successful = True
      else:
        result.successful = False
      results.append(result)
    i += 1
  return results

def _upload_fields():
  '''
    :returns: Returns a list of tuples with name of the file & stream as value.
  '''
  result = []
  for key, value in request.files.iteritems():
    if type(value) is not unicode:
      result.append((key, value))
  return result

def get_field_size(field):
  '''
    :param field:

    :returns:
  '''
  try:
    field.seek(0, 2) # Seek to the end of the file
    size = field.tell() # Get the position of EOF
    field.seek(0) # Reset the file position to the beginning
    return size
  except:
    return 0

def validate(field,
    accept_file_types=UPLOAD_ACCEPT_FILE_TYPES,
    min_file_size=UPLOAD_MIN_FILE_SIZE,
    max_file_size=UPLOAD_MAX_FILE_SIZE):
  '''Validates a file input based on size & type. If validation fails, adds
  an error property to the field arg dict.

    :param field:
    :param accept_file_types:
    :param min_file_size:
    :param max_file_size:

    :returns:
  '''
  if field.size < UPLOAD_MIN_FILE_SIZE:
    field.error_msg = 'min_file_size'
  elif field.size > UPLOAD_MAX_FILE_SIZE:
    field.error_msg = 'max_file_size'
  # only allow images to be posted to this handler
  elif not accept_file_types.match(field.type):
    field.error_msg = 'accept_file_types'
  else:
    return True
  return False

def write_to_blobstore(data, mime_type, name=None):
  '''Writes a file to the App Engine blobstore and returns an instance of a
  BlobKey if successful.

    :param data:
    :param mime_type:
    :param name:

    :returns:
  '''
  if not name:
    name = ''.join(random.choice(string.letters)
      for x in range(DEFAULT_NAME_LEN))
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
    logging.exception('Exception writing to the blobstore: %s',
      traceback.format_exc())

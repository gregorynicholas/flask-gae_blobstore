"""
  `dev_appserver.py .
  `curl -X POST -F 'file=@test.jpg' http://localhost:8080/test`
"""

from flask import json, request
from flask import Flask
import gae_blobstore
import logging

app = Flask(__name__)
app.debug = True

@app.route('/test', methods=gae_blobstore.OPTIONS)
@gae_blobstore.upload_blobs()
def test(blobs):
  logging.info(request.form)
  return json.dumps(blobs.to_dict())

if __name__ == '__main__':
  app.run()

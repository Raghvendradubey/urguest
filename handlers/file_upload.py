# Copyright 2013 Google Inc. All Rights Reserved.


"""A sample app that operates on GCS files with blobstore API."""

from __future__ import with_statement

from google.appengine.api import images
from google.appengine.api.images import delete_serving_url
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

from lib import cloudstorage as gcs
import create_bucket
import json
import re
import time
import urllib

from lib import utils
from lib.base_handler import BaseHandler
from models import pg_ad as pg_model
import config

import logging

def image_url(host_url,blob_key):
  """" returns url of the image """
  url = images.get_serving_url(
                    blob_key,
                    secure_url=host_url.startswith(
                        'https'
                    )
                )
  return url  
    
def image_delete_url(host_url, path,  blob_key):
  """" returns delete image url """
  return host_url + '/' +  path + '?key=' + urllib.quote(blob_key, '')


def image_thumbnail_url(url):
  """" returns image thumbnail url """
  return url + config.THUMBNAIL_MODIFICATOR

def CreateFile(filename):
  """Create a GCS file with GCS client lib.

  Args:
    filename: GCS filename.

  Returns:
    The corresponding string blobkey for this GCS file.
  """
  with gcs.open(filename, 'w') as f:
    f.write('abcde\n')

  blobstore_filename = '/gs' + filename
  return blobstore.create_gs_key(blobstore_filename)
  
def validate(file):
  """
  validate file

  Args:
    file : file to validate
  
  return:
    if validated then
      True
    else
      False  
  """
  if file['size'] < config.MIN_FILE_SIZE:
    file['error'] = 'File is too small'
  elif file['size'] > config.MAX_FILE_SIZE:
    file['error'] = 'File is too big'
  elif not (config.ACCEPT_FILE_TYPES).match(file['type']):
    file['error'] = 'Filetype not allowed'
  else:
    return True
  return False

def get_file_size(file):
  """ get file size

  Args:
    file : file

  return:
    size : size of the file  
  """
  file.seek(0, 2)  # Seek to the end of the file
  size = file.tell()  # Get the position of EOF
  file.seek(0)  # Reset the file position to the beginning
  return size

def write_blob(data, info):
  """ write file into blobs

  Args:
    data : file data to write into blob
    info : information about file like name etc
  
  return:
    blob key  
  """
  with gcs.open(info, 'w') as f:
    f.write(data)

  blobstore_filename = '/gs' + info
  return blobstore.create_gs_key(blobstore_filename)            


def upload(host_url,fieldStorage):
  """ create image serving url after upload

  return:
    result : file info
  """
  logging.info('2 %s' % fieldStorage)
  result = {}
  result['name'] = re.sub(
    r'^.*\\',
    '',
    fieldStorage.filename
  )
  result['type'] = fieldStorage.type
  result['size'] = get_file_size(fieldStorage.file)
  if validate(result):
    img_name = utils.random_string(size = config.RANDOM_IMAGE_NAME_SIZE)  
    gcs_filename = create_bucket.BUCKET + '/' + img_name
    blob_key = str(
        write_blob(fieldStorage.value, gcs_filename)
    )
    logging.info('4 %s' % blob_key)
    result['deleteType'] = 'DELETE'
    result['deleteUrl'] = image_delete_url(host_url, 'upload',blob_key)
    if (config.IMAGE_TYPES.match(result['type'])):
      try:
        result['url'] = image_url(host_url, blob_key)
        result['thumbnailUrl'] = image_thumbnail_url(result['url'])
      except:  # Could not get an image serving url
        pass
    if not 'url' in result:
      result['url'] = host_url + \
            '/' + blob_key + '/' + urllib.quote(
                result['name'].encode('utf-8'), '')

  return result, blob_key
    
def delete_blob(blob_key):
  """ delete blob key """
  blobstore.delete(blob_key)            


class UploadHandler(BaseHandler):
    
  def initialize(self, request, response):
    """ initialize headers 
    
    Args:
      request : request argument
      response : response argument
    """
    super(UploadHandler, self).initialize(request, response)
    self.response.headers['Access-Control-Allow-Origin'] = '*'
    self.response.headers[
        'Access-Control-Allow-Methods'
    ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
    self.response.headers[
        'Access-Control-Allow-Headers'
    ] = 'Content-Type, Content-Range, Content-Disposition'

  def handle_upload(self):
    """ create image serving url after upload
    
    return:
      result : file info
    """
    results = []
    dict_keys = {}
    host_url = self.request.host_url
    logging.info('1 %s' % self.request.POST.items())
    for name, fieldStorage in self.request.POST.items():
        if type(fieldStorage) is unicode:
            continue
        result, blob_key = upload(host_url, fieldStorage)
        
        if self.session.get('pg_id') is not None:
          pg_id = self.session.get('pg_id')
          pg = pg_model.AddNewPg(pg_id)
          serving_url = pg.pg_images
          serving_url.append(result['url'])
          pg.pg_images = serving_url
          pg.put()
        else:  
          random_str = utils.random_string()
          serving_url  = [result['url']]
          pg = pg_model.AddNewPg(random_str)
          pg.pg_images.extend(serving_url)
          pg.put()
          self.session['pg_id'] = random_str
        
        """if self.session.get('keys') is not None:
          keys = self.session.get('keys')
          keys[blob_key] = [
                             result['url'],
                             result['thumbnailUrl'],
                             result['name'],
                             result['size'],
                             result['deleteUrl'],
                             result['deleteType']
                           ]
          self.session['keys'] = keys
        else:
          dict_keys[blob_key] = [
                                 result['url'],
                                 result['thumbnailUrl'],
                                 result['name'],
                                 result['size'],
                                 result['deleteUrl'],
                                 result['deleteType']
                                    ]
          self.session['keys'] = dict_keys"""
        results.append(result)
        logging.info('6 %s' % result)
    return results    

  def post(self):
    if (self.request.get('_method') == 'DELETE'):
        return self.delete()
    result = {'files': self.handle_upload()}
    s = json.dumps(result, separators=(',', ':'))
    redirect = self.request.get('redirect')
    if redirect:
        return self.redirect(str(
            redirect.replace('%s', urllib.quote(s, ''), 1)
        ))
    if 'application/json' in self.request.headers.get('Accept'):
        self.response.headers['Content-Type'] = 'application/json'
    self.response.write(s)
    
  def delete(self):
    """ delete blob key """
    key = self.request.get('key') or ''
    delete_blob(key)
    #keys = self.session.get('keys')
    #keys.pop(key, None)
    #self.session['keys'] = keys
    if self.session.get('pg_id') is not None:
      pg_id = self.session.get('pg_id')
      pg = ndb.Key('Pg', pg_id)
      pg = pg.get()

      logging.info("keys are %s" % key)
      for i in pg.pg_images:
        logging.info("image key are %s" % i)
    pg.pg_images.remove(key)
    pg.pg_image_no =- 1
    pg.put()
    img_key = key.split('/')
    blob_key_for_div = img_key[-1]
    s = json.dumps({blob_key_for_div: True}, separators=(',', ':'))
    if 'application/json' in self.request.headers.get('Accept'):
        self.response.headers['Content-Type'] = 'application/json'
    self.response.write(s)  
    

class UploadEditHandler(BaseHandler):
    
  def initialize(self, request, response):
    """ initialize headers 
    
    Args:
      request : request argument
      response : response argument
    """
    super(UploadEditHandler, self).initialize(request, response)
    self.response.headers['Access-Control-Allow-Origin'] = '*'
    self.response.headers[
        'Access-Control-Allow-Methods'
    ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
    self.response.headers[
        'Access-Control-Allow-Headers'
    ] = 'Content-Type, Content-Range, Content-Disposition'

  def handle_upload(self, pg):
    """ create image serving url after upload
    
    return:
      result : file info
    """
    results = []
    host_url = self.request.host_url
    logging.info('1 %s' % self.request.POST.items())
    for name, fieldStorage in self.request.POST.items():
      if type(fieldStorage) is unicode:
        continue
      result, blob_key = upload(host_url, fieldStorage)
      pg.pg_images.append(result['url'])
      pg.pg_image_no =+ 1
      pg.put()
      time.sleep(0.1) # need little time to update datastore
      results.append(result)
    return results    

  def post(self, pg_id):
    logging.info('pg id is %s', pg_id)  
    pg = ndb.Key('Pg',int(pg_id))
    pg = pg.get()  
    if (self.request.get('_method') == 'DELETE'):
        return self.delete(pg)
    result = {'files': self.handle_upload(pg)}
    s = json.dumps(result, separators=(',', ':'))
    redirect = self.request.get('redirect')
    if redirect:
      return self.redirect(str(
            redirect.replace('%s', urllib.quote(s, ''), 1)
      ))
    if 'application/json' in self.request.headers.get('Accept'):
      self.response.headers['Content-Type'] = 'application/json'
    self.response.write(s)
    
  def delete(self, pg):
    """ delete blob key """
    key = self.request.get('key') or ''
    logging.info("keys are %s", key)
    #url = image_url(self.request.host_url, key)
    #gcs_filename = create_bucket.BUCKET + '/' + 'pg4.jpeg'
    #cloudstorage_file_name = '/bucket/image.jpg'
    #gcs_path = '/gs'+ gcs_filename
    #key =  blobstore.create_gs_key(gcs_path)
    #logging.info('url is %s', url)
    #logging.info('key is %s', key)
    #delete_blob(key)
    #delete_serving_url(key)
    pg.pg_images.remove(key)
    pg.pg_image_no =- 1
    pg.put()
    img_key = key.split('/')
    blob_key_for_div = img_key[-1]
    s = json.dumps({blob_key_for_div: True}, separators=(',', ':'))
    if 'application/json' in self.request.headers.get('Accept'):
      self.response.headers['Content-Type'] = 'application/json'
    self.response.write(s)      


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):

  def get(self):
    blob_key = CreateFile(create_bucket.BUCKET + '/blobstore_serving_demo')
    self.send_blob(blob_key)


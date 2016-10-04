# -*- coding: utf-8 -*-
"imports are going here"
import time
import logging

from google.appengine.api import taskqueue
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.api.images import delete_serving_url
from google.appengine.ext import blobstore

import webapp2

from file_upload import image_url, image_delete_url,image_thumbnail_url
from lib import utils
from lib.base_handler import BaseHandler
from lib.base_handler import send_message
from lib.base_handler import sign_up
from lib.base_handler import null_cache
from models import pg_ad as pg_model
from models import pg_location as location_model
from models import pg_user as user_model
from models import pg_message
from search import PG_INDEX
import forms
import config


class PgDetail(BaseHandler):
  """ ad detail
  
  Args:
    BaseHandler : Base class for handler
  """
  def _check_sharing(self, pg):
      """ check how many sharing availabale in pg
      
      Args:
        pg : pg instance
        
      return:
        SHARING : list of sharing  
      """
      if pg.three_sharing_remaining and pg.two_sharing_remaining:
        SHARING = forms.SHARING      
      elif pg.three_sharing_remaining:
        SHARING = [
                   config.SHARING_TYPES[1]
                  ]
        SHARING.insert(0, ('', 'You Wish To Share'))
      elif pg.two_sharing_remaining:
        SHARING = [
                   config.SHARING_TYPES[0]
                  ]
        SHARING.insert(0, ('', 'You Wish To Share'))
      else:
        SHARING = forms.SHARING    
      return SHARING  
      
  def get(self, pg_id):
    """ Handlers GET/Detail
   
    render:
     pg_detail.html : pg detail html
    """
    pg = ndb.Key(urlsafe=pg_id)

    #pg = ndb.Key('Pg', pg_id)
    pg = pg.get()
    logging.info("pg is %s", pg)
    sheets = pg_model.GetPgSheet(pg.key)
    is_allowed_to_edit = (self.is_admin)
    self.message_form.is_message.data = True
    sharing = self._check_sharing(pg)       
    self.form.sharing.choices = sharing
    params = {
        'page_title': pg.pg_title,
        'is_pg_detail': True,
        'is_allowed_to_edit' : is_allowed_to_edit,
        'pg': pg,
        'sheets' : sheets,
        'message_form' : self.message_form
    }
    self.render('pg_detail.html', **params)
    
  def post(self, pg_id):
    """ Handlers POST/Detail
   
    render:
     pg_detail.html : pg detail html
    """
    if self.message_form.is_message.data:
      if not self.message_form.validate():
        return self.get(pg_id)
      user_message = self.message_form.description.data
      user = self.logged_in_user('user_id')
      pg = ndb.Key("Pg", pg_id)
      pg = pg.get()
      pg_message.AddNewMessage(user.key, pg.key, user_message, owner_message = None)
      params = {
                'message' : 'Thanks for Your Query'
               }
      self.render('thank_you.html', **params)
    else:  
      pg = ndb.Key("Pg", pg_id)
      pg = pg.get()
      sharing = self._check_sharing(pg)       
      self.form.sharing.choices = sharing  
      if not self.form.validate():
        return self.get(pg_id)
      user_email = self.form.user_email.data
      sharing = int(self.form.sharing.data)
      user = user_model.GetUserByEmailId(user_email)
      if user:
        if pg.key not in user.requested_pg:
          user.requested_pg.append(pg.key)
          user.put()     
        sheets = pg_model.GetPgSheet(pg.key,sharing=sharing)
        if sheets:
          user.requested_pg_sheet.append((sheets.pop()).key)
          user.put()
          sheet = sheets.pop()  
          sheet.requested_user.append(user.key)
          sheet.put()
          url = self.request.url  
          send_message(config.PG_SUPPORT_MAIL, config.PG_REQUEST_SUBJECT, 
                       config.PG_REQUEST_MESSAGE(user_email,sharing,url), config.PG_SUPPORT_MAIL)
          params = {
            'message' : 'Thanks for your Request'
          }
          self.render('thank_you.html', **params)
          pg.pg_request.append(user.key)
          pg.put()
        else:
          params = {
                    'message' : 'Sorry Requested Sheet is not available'
                  }
          self.render('thank_you.html', **params)  
      # if user does not exist then create a new one
      else:
        # not an Oauth sign up  
        auth_id = None
        name = None  
        user = sign_up(self, auth_id, name, user_email)
        if pg.key not in user.requested_pg:
          user.requested_pg.append(pg.key)
          user.put()
        sheets = pg_model.GetPgSheet(pg.key,sharing=sharing)
        if sheets:
          user.requested_pg_sheet.append((sheets.pop()).key)
          user.put()
          sheet = sheets.pop()  
          sheet.requested_user.append(user.key)
          sheet.put()
          pg_model.AddNewContact(pg.key, user.key,
                                 config.PG_SUPPORT_MAIL)
          url = self.request.url  
          send_message(config.PG_SUPPORT_MAIL, config.PG_REQUEST_SUBJECT, 
                       config.PG_REQUEST_MESSAGE(user_email,sharing,url), config.PG_SUPPORT_MAIL)
          params = {
            'message' : 'Thanks for your Request'
          }
          self.render('thank_you.html', **params)
          pg.pg_request.append(user.key)
          pg.put()

        else:
          params = {
                    'message' : 'Sorry Requested Sheet is not available'
                  }
          self.render('thank_you.html', **params)

  @webapp2.cached_property
  def form(self):
    """It is used to get the book pg form
    Return:
      BookPgForm: book pg form
    """
    return forms.BookPgForm(self)

  @webapp2.cached_property
  def message_form(self):
    """send message from user
    Return:
      UserMessageForm: message form
    """
    return forms.UserMessageForm(self)

class PgEdit(BaseHandler):
  """ ad edit
  
  Args:
    BaseHandler : Base class for handler
  """
  def get(self, pg_id):
    """ Handlers GET/Detail
   
    render:
     pg_detail.html : pg detail html
    """
    dict_keys = {}
    pg = ndb.Key('Pg', pg_id)
    pg = pg.get()
    is_allowed_to_edit = (self.is_admin)
    logging.info("pg id before submit is %s", pg.key.id())  
    path = webapp2.uri_for('upload_edit', pg_id=str(pg.key.id()))
    for img in pg.pg_images:
      img_list = img.split('/')
      blob_key_for_div = img_list[-1]
      blob_key = img
      dict_keys[blob_key_for_div] = [
                             img,
                             image_thumbnail_url(img),
                             'abc',
                             '123',
                             image_delete_url(self.request.host_url,path, blob_key),
                             'DELETE'
                            ]

    params = {
        'page_title': pg.pg_title,
        'is_pg_edit': True,
        'is_allowed_to_edit' : is_allowed_to_edit,
        'pg': pg,
        'pg_id':pg.key.id(),
        'keys': dict_keys
    }
    self.render('pg_detail.html', **params)

  def post(self, pg_id):
    """ method to get the pg data and submit it to datastore """
    pg = ndb.Key(urlsafe=pg_id)
    pg = pg.get()

   # Values to retrieve from request and how to parse/process/validate them.
    attribute_parsers = dict(
        pg_title=None,
        pg_price=utils.parse_str_to_int,
        pg_detail=None,
        pg_city=None,
        pg_street_address=None,
        three_sharing_remaining=utils.parse_str_to_int,
        two_sharing_remaining=utils.parse_str_to_int
        
    )

    for attribute, parser in attribute_parsers.iteritems():
      if not hasattr(pg, attribute):
        raise ValueError('No such pg field: %s' % attribute)
      field_name = utils.to_camel_case(attribute)
      logging.info('field name is %s', field_name)
      field_value = self.request.get(field_name) or None
      logging.info('field value is %s', field_value)
      if field_value:
        if parser:
          field_value = parser(field_value)
        if field_value is not None:
          setattr(pg, attribute, field_value)

    pg.put()
    logging.info("successfully edited")
    
    
class PgDelete(BaseHandler):
  """ pg delete
  
  Args:
    BaseHandler : Base class for handler
  """
  def get(self, pg_id):
    """ Handlers GET/Detail """
    pg = ndb.Key('Pg', int(pg_id))
    pg = pg.get()
    is_allowed_to_edit = (self.is_admin)
    if is_allowed_to_edit and pg:
      #for images in pg.pg_images:
        #  img = images.split('/')
         # blob_key = img[-1]
         # logging.info('blob key is %s', blob_key)
          #blobstore.delete(str(blob_key))
        #  delete_serving_url(blob_key)
         # time.sleep(0.1) # need little time to update datastore
          
      pg.key.delete()
      # When saving a new link, it needs to be indexed for search, like this:
      taskqueue.add(url='/taskqueue/delete-index',
                    queue_name='indexing',
                    params=dict(document_id=pg.key.urlsafe(),
                                index=PG_INDEX))
    self.local_redirect_to('home')    
            
  
class PgRequestUser(BaseHandler):
  """ Handler for Pg requests to Add and Remove requests """
  def post(self, pg_id=None):
    """ Method to add and remove requests
    only admin is allowed to add and remove the requests
    Args:
      pg_id : Pg Id
    """  
    request_user_key = self.request.get('requestUser')
    remove_user_key = self.request.get('removeuser')
    add_user = self.request.get('containsAddUser')
    remove_user = self.request.get('containsRemoveUser')
    sharing = int(self.request.get('sharing'))
    logging.info("sharing is %s", sharing)
    pg = ndb.Key('Pg', int(pg_id))
    pg = pg.get()    
    if not pg:
      self.abort(404)
    is_allowed_to_edit = (self.is_admin)
    if is_allowed_to_edit:  
      if add_user:  
        user_key = ndb.Key(urlsafe=request_user_key)  
        if user_key in pg.pg_member:
          pg.pg_member.remove(user_key)
          
          user = user_key.get()
          user.pg = None
          user.put()
          # if user is member of pg then then get the sheet and free it
          sheets = pg_model.GetPgSheet(pg.key,user=user)
          if sheets:
            sheet = sheets.pop()
            if sheet.key not in user.requested_pg_sheet:
              user.requested_pg_sheet.append(sheet.key)
              user.put()
            sheet.user = None
            sheet.is_alloted = False
            sheet.put()
          pg.pg_request.append(user_key)
          # update pg remaining sheets
          if sharing == config.THREE_SHARING:
            pg.three_sharing_remaining = pg.three_sharing_remaining + 1
          if sharing == config.TWO_SHARING:
            pg.two_sharing_remaining = pg.two_sharing_remaining + 1  
        else:
          pg.pg_member.append(user_key)
          user = user_key.get()
          user.pg = pg.key
          if pg.key in user.requested_pg:
            user.requested_pg.remove(pg.key)
          user.put()
          sheets = pg_model.GetPgSheet(pg.key,sharing=sharing)
          if sheets:
            for sheet in sheets:
              if sheet.key in user.requested_pg_sheet:
                logging.info("sheets are %s", (sheets.pop()).key)
                logging.info("user requested pg %s", user.requested_pg_sheet)
                user.requested_pg_sheet.remove(sheet.key)
                user.put()
            sheet = sheets.pop()
            sheet.user = user.key
            sheet.is_alloted = True
            sheet.put()
          # update pg remaining sheets
          if sharing == config.THREE_SHARING:
            pg.three_sharing_remaining = pg.three_sharing_remaining - 1
          if sharing == config.TWO_SHARING:
            pg.two_sharing_remaining = pg.two_sharing_remaining - 1 
          pg.pg_request.remove(user_key)
      if remove_user:
        user_key = ndb.Key(urlsafe=remove_user_key)   
        if user_key in pg.pg_member:
          pg.pg_member.remove(user_key)
          user = user_key.get()
          user.pg = None
          user.put()
          pg.pg_request.append(user_key)
          # if user is member of pg then then get the sheet and free it
          sheets = pg_model.GetPgSheet(pg.key,user=user_key)
          logging.info('sheets are %s', sheets)
          if sheets:
            sheet = sheets.pop()
            if sheet.key in user.requested_pg_sheet:
              user.requested_pg_sheet.remove(sheet.key)
              user.put()
            sheet.user = None
            sheet.is_alloted = False
            sheet.put()
          pg.pg_request.append(user_key)
          # update pg remaining sheets
          if sharing == config.THREE_SHARING:
            pg.three_sharing_remaining = pg.three_sharing_remaining + 1
          if sharing == config.TWO_SHARING:
            pg.two_sharing_remaining = pg.two_sharing_remaining + 1
      pg.put()            
      
      
class PgPost(BaseHandler):
  """posting an pg
  Args:
    BaseHandler : base handler class
  """
  def get(self):
    """method to render pg post html
    render:
      pg_post.html : pg post html
    """
    dict_keys = {}
    if self.session.get('pg_id') is not None:
      pg_id = self.session.get('pg_id')
      pg = ndb.Key('Pg', pg_id)
      pg = pg.get()
      for img in pg.pg_images:
        img_list = img.split('/')
        blob_key_for_div = img_list[-1]
        blob_key = img
        dict_keys[blob_key_for_div] = [
                                       img,
                                       image_thumbnail_url(img),
                                       'abc',
                                       '123',
                                       image_delete_url(self.request.host_url,'upload', blob_key),
                                       'DELETE'
                                      ]
    else:
      pg_id = None  

    LOCATION = [
      ((location.city_name).lower(), (location.city_name))
      for location in location_model.GetCities()
    ]
    logging.info("location are %s", LOCATION)
    LOCATION.insert(0, ('', 'Choose One Location...'))
    self.form.location.choices = LOCATION
    
    params = {
        'page_title': 'Add PG',      
        'is_pg_post' : True,
        'keys' : dict_keys,
    }
    self.render('pg_form_step1.html', **params)

  def post(self):
    """method to add ad_post data
    redirect:
          : ad_detail page
    """
    LOCATION = [
      ((location.city_name).lower(), (location.city_name))
      for location in location_model.GetCities()
    ]
    LOCATION.insert(0, ('', 'Choose One Location...'))
    self.form.location.choices = LOCATION
    if not self.form.validate():
      return self.get()

    location = self.form.location.data
    location_key = ndb.Key('City', location.lower())
    title = self.form.title.data
    description = self.form.description.data
    street_address = self.form.street_address.data
    price = self.form.price.data
    three_sharing = int(self.form.sharing_three.data)
    two_sharing = int(self.form.sharing_two.data)
    pg_type = int(self.form.pg_type.data)

    keys = {}
    if self.session.get('pg_id') is not None:
      pg_id = self.session.get('pg_id')
      pg = ndb.Key('Pg', pg_id)
      pg = pg.get()
        

    images = len(pg.pg_images)

    user = self.logged_in_user('user_id')
    if user:
      user = user.key  
    pg = pg_model.AddNewPg(pg_id, title, description, int(price),
                           street_address, images, user,
                           three_sharing, two_sharing, pg_type,
                           location_key)
    time.sleep(0.1)
    
    three_sharing_list = []
    for sharing in range(three_sharing):
      three_sharing = pg_model.AddNewSharingSheet(pg.key, 3)
      three_sharing_list.append(three_sharing.key)
      time.sleep(0.1) # need little time to update
    
    two_sharing_list = []
    for sharing in range(two_sharing):
      two_sharing = pg_model.AddNewSharingSheet(pg.key, 2)
      two_sharing_list.append(two_sharing.key)
      time.sleep(0.1) # need little time to update

    pg.pg_two_sharing_sheet.extend(two_sharing_list)
    pg.pg_three_sharing_sheet.extend(three_sharing_list)

    pg.put()
    logging.info("before indexing")
    # When saving a new link, it needs to be indexed for search, like this:
    if user:
      # if user in session then remove pg id from session
      self.session.pop('pg_id')
      taskqueue.add(url='/taskqueue/index-single-pg',
                    queue_name='indexing',
                    params=dict(pg_id=pg.key.urlsafe()))
      self.local_redirect_to('pg_detail', pg_id=pg.key.id())
    else:
      self.local_redirect_to('sign_up')
      

  @webapp2.cached_property
  def form(self):
    """It is used to get the ad_post form
    Return:
      AdPostForm: ad_post form
    """
    return forms.AdPostForm(self)

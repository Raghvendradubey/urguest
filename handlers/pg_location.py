# -*- coding: utf-8 -*-
"imports are going here"
import logging
import time

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import webapp2

import forms
from lib.base_handler import BaseHandler
from lib.base_handler import null_cache


class LocationSubmit(BaseHandler):
  """ submit ad 
  
  Args:
    BaseHandler : Base class for handler
  """
  @null_cache
  def get(self):
    """ Handlers GET/Submit
   
   render:
     ad_form_step1.html : submit ad form
    """
    if not self.is_admin:
      self.abort(404)

    params = {
        'page_title': 'Submit Ad',
        'is_location_submit': True,
    }
    self.render('add_location1.html', **params)

  @null_cache
  def post(self):
    """ method to get the ad data and submit it to datastore
   
    render:
      ad_detail.html : ad detail html
    """
    if not self.form.validate():
      return self.get()
    else:
      location = self.form.location.data
      category.put()

      # PLEASE READ #
      # When saving a new event, it needs to be indexed for search, like this:
      taskqueue.add(url='/taskqueue/index-single-location',
                    queue_name='indexing',
                    params=dict(category_id=category.key.urlsafe()))

      time.sleep(1)  # Needs a little time to update.

      params = {
        'page_title': 'Submit Ad',
        'is_location_submit': True,
      }
      self.render('thanks.html', **params)

  @webapp2.cached_property
  def form(self):
    """ad form 
    
    Return:
      AddAdForm: Method of forms
    """
    return forms.AddLocationForm(self)

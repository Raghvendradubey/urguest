# -*- coding: utf-8 -*-
#!/usr/bin/python
""" Imports """
from lib.base_handler import BaseHandler

    
class OwnerHandler(BaseHandler):
  """ Faq page """
  def get(self):
    """ get the request for Property Owner page
    render :
      owner.html : property owner page 
    """
    params = {
      'page_title': 'Property Owner',
      'is_owner': True,
    }
    self.render('owner.html', **params)    
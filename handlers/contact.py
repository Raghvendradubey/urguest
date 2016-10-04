# -*- coding: utf-8 -*-
#!/usr/bin/python
""" Imports """
from lib.base_handler import BaseHandler

    
class ContactHandler(BaseHandler):
  """ contact page """
  def get(self):
    """ get the request for contact page
    render :
      contact_us.html : about page 
    """
    params = {
      'page_title': 'Contact Us',
      'is_contact_us': True,
    }
    self.render('contact_us.html', **params)    

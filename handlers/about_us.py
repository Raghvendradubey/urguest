# -*- coding: utf-8 -*-
#!/usr/bin/python
""" Imports """
from lib.base_handler import BaseHandler

    
class AboutUsHandler(BaseHandler):
  """ about page """
  def get(self):
    """ get the request for about page
    render :
      about_us.html : about page 
    """
    params = {
      'page_title': 'About Us',
      'is_about_us': True,
    }
    self.render('about_us.html', **params)    

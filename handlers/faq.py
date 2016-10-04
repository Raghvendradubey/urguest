# -*- coding: utf-8 -*-
#!/usr/bin/python
""" Imports """
from lib.base_handler import BaseHandler

    
class FaqHandler(BaseHandler):
  """ Faq page """
  def get(self):
    """ get the request for Faq page
    render :
      faq.html : faq page 
    """
    params = {
      'page_title': 'FAQ',
      'is_faq': True,
    }
    self.render('faq.html', **params)    
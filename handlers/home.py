# -*- coding: utf-8 -*-
#!/usr/bin/python
""" Imports """
from lib.base_handler import BaseHandler
from models import pg_ad as pg_models


class HomeHandler(BaseHandler):
  """ Home page """
  def get(self):
    """ get the request for home
    render :
      home_page.html : home page 
    """
    pgs = pg_models.GetPgs()
    params = {
      'page_title': 'URGuest Home',
      'is_home': True,
      'pgs' : pgs
    }
    self.render('home_page.html', **params)
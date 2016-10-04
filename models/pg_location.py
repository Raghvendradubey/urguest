# -*- coding: utf-8 -*-
""" Imports """
from google.appengine.ext import ndb


class City(ndb.Model):
  """ cities"""
  city_name = ndb.StringProperty()
  added_by = ndb.KeyProperty()
  added_on = ndb.DateTimeProperty(auto_now_add=True)
  
  
def AddCity(city):
  """Add New City
  Args:
    city : new city name
  
  Return:
   new_city :  city key
  """
  new_city = City.get_or_insert(
      city.lower(),
      city_name=city
  )
  new_city = new_city.put()
  return new_city


def GetCities():
  """Returns list of location object
  
  need to filter according to city but for now it is default for Delhi/Ncr
  """
  return City.query().fetch()

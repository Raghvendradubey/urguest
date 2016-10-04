# -*- coding: utf-8 -*-
""" Imports """
from google.appengine.ext import ndb

from models.pg_user import User
from models.pg_location import City
from config import SHARING
from config import PG_TYPES_MODEL


class Pg(ndb.Model):
  """Pg Model to store category ad """
  pg_title = ndb.StringProperty()
  pg_price = ndb.IntegerProperty()
  pg_detail = ndb.TextProperty()
  pg_images = ndb.StringProperty(repeated=True)
  # user requested for pg allotment
  pg_request = ndb.KeyProperty(repeated=True)
  pg_member = ndb.KeyProperty(repeated=True)

  # pg's two sharing sheet keys
  pg_two_sharing_sheet = ndb.KeyProperty(repeated=True)

  # pg's 3 sharing sheet keys
  pg_three_sharing_sheet = ndb.KeyProperty(repeated=True)

  pg_type = ndb.IntegerProperty(choices=PG_TYPES_MODEL.keys())
  pg_city = ndb.KeyProperty(kind=City)
  pg_street_address = ndb.StringProperty()
  pg_image_no = ndb.IntegerProperty(default=0)
  
  three_sharing_sheet = ndb.IntegerProperty(default=0)
  three_sharing_remaining = ndb.IntegerProperty()
  
  two_sharing_sheet = ndb.IntegerProperty(default=0)
  two_sharing_remaining = ndb.IntegerProperty()
  is_pg_full = ndb.BooleanProperty(default=False)
  is_verified = ndb.BooleanProperty(default=False)
  added_by = ndb.KeyProperty(kind=User)
  clicks = ndb.IntegerProperty(default=0)
  added_on = ndb.DateTimeProperty(auto_now_add=True)

  def pgImage(self):
    """ first image of pg
    
    return:
      first image of pg
    """  
    return self.pg_images  

  def getCity(self):
    """ get city of current pg
    
    return:
      city instance
    """  
    return self.pg_city.get()

  
class SharingSheet(ndb.Model):
  """Sharing sheets in pg (eg : could be 3 sharing or 2 sharing) """ 
  pg = ndb.KeyProperty(kind=Pg) 
  user = ndb.KeyProperty(kind=User) 
  sharing = ndb.IntegerProperty(choices=SHARING.keys())

  is_alloted = ndb.BooleanProperty(default=False)
  requested_user = ndb.KeyProperty(repeated=True)
  added_on = ndb.DateTimeProperty(auto_now_add=True)
  

class PgContact(ndb.Model):
  """ Contacts for the Pg """
  pg = ndb.KeyProperty(kind=Pg)
  sender = ndb.KeyProperty(kind=User)
  receiver = ndb.StringProperty()
  added_on = ndb.DateTimeProperty(auto_now_add=True)


def AddNewSharingSheet(pg, sharing):
  """Add new sharing sheet for the pg.

  Args:
    pg : pg key
    sharing : sharing sheet
  """
  pg_sharing = SharingSheet(
      pg=pg,
      sharing=sharing,
  )
  pg_sharing.put()
  return pg_sharing


def AddNewContact(pg, sender, receiver):
  """Add new contacts for the pg.

  Args:
    pg : pg key
    sender : sender user key
    receiver : receiver of the mail
    receiver_random_mail : receiver random mail
  """
  pg_contact = PgContact(
      pg=pg,
      sender=sender,
      receiver=receiver
  )
  pg_contact.put()
  

def AddNewPg(pg_id,pg_title=None, pg_detail=None, pg_price=None,
             street_address=None, images=None,user_id=None, 
             three_sharing=None, two_sharing=None, pg_type=None, city_key=None):
  """Adding a new pg to the datastore model.

  Args:
    pg_title : pg title
    pg_detail : pg detail
    pg_price : price of pg
    street_address : pg location
    serving_url : list of image serving url
    images : number of images in pg
    user_id : user id
    city_key : city key
    
  Return:
    new_pg : newly added pg key  
  """
  new_pg = Pg.get_or_insert(pg_id)
  new_pg.pg_city = city_key
  new_pg.pg_title = pg_title
  new_pg.pg_detail = pg_detail
  new_pg.pg_price = pg_price
  new_pg.pg_street_address = street_address
  new_pg.pg_image_no = images
  new_pg.two_sharing_sheet = two_sharing
  new_pg.three_sharing_sheet = three_sharing
  new_pg.three_sharing_remaining = three_sharing
  new_pg.two_sharing_remaining = two_sharing
  new_pg.pg_type = pg_type
  new_pg.added_by = user_id
  new_pg.put()
  return new_pg


def GetPgs():
  """Returns a datastore object with all ads."""
  pg = Pg.query().order(Pg.added_on)
  return pg.fetch()


def GetPgSheet(pg,sharing=None, user=None):
  """Returns all sheets of the pg which is not alloted to any user.
  
  Args:
    pg : pg key
    sharing : sharing sheet
    
  Returns:
    instance of sheets  
  """
  if user:
    sheet = SharingSheet.query().filter(SharingSheet.pg == pg).filter(SharingSheet.user == user).filter(SharingSheet.is_alloted == True)      
      
  elif sharing:
    sheet = SharingSheet.query().filter(SharingSheet.pg == pg).filter(SharingSheet.sharing == sharing).filter(SharingSheet.is_alloted == False)
  else:
    sheet = SharingSheet.query().filter(SharingSheet.pg == pg)      
  return sheet.fetch()


def GetUserPgs(user):
  """Returns a datastore object with all pgs of user.
  
  Args:
    user : user key
    
  Returns:
    instance of user pgs  
  """
  pg = Pg.query().filter(Pg.user == user).order(Pg.added_on)
  return pg.fetch()
  
  
def GetPgContact(mail):
  """ get sender and receiver email for Pg from email
  
  Args:
    mail : email of the user
  """
  return PgContact.query().filter(PgContact.sender == mail).get()
  
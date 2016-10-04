# -*- coding: utf-8 -*-
""" Imports """
from google.appengine.ext import ndb

from models.pg_user import User
from models.pg_ad import Pg


class Message(ndb.Model):
  """ Messages send to Pg Owner by Pg Member """
  user = ndb.KeyProperty(kind=User)
  pg=ndb.KeyProperty(kind=Pg) 
  member_message = ndb.StringProperty(repeated=True)
  owner_message = ndb.StringProperty(repeated=True)
     
     
def AddNewMessage(user, pg, member_message=None, owner_message=None):
  """Adding a new message i.e sent by owner or member.

  Args:
    user : member of the pg
    pg : pg key
    member_message : message of member
    owner_message : message from the owner
  """
  new_pg = Message(
      user=user,
      pg=pg
  )
  if member_message:
    new_pg.member_message.append(member_message)
  if owner_message:  
    new_pg.owner_message.append(owner_message)
  new_pg.put()
  
  
def GetMessageByUser(user):
  """Get message by user key
  Args:
    user : key of user
  Return:
    message instance  
  """
  return Message.query().filter(Message.user == user).fetch()  
     
# -*- coding: utf-8 -*-
"Imports are going here"
from google.appengine.ext import ndb

# from webapp2_extras.appengine.auth.models import Unique


class User(ndb.Model):
  """ User Model to store user values """
  user_auth_id = ndb.StringProperty()
  user_id = ndb.StringProperty()
  user_name = ndb.StringProperty()
  user_email = ndb.StringProperty()
  user_password = ndb.StringProperty()
  user_avatar = ndb.BlobKeyProperty()
  is_email_verified = ndb.BooleanProperty()
  last_logged_in = ndb.DateTimeProperty()
  last_modified = ndb.DateTimeProperty()
  
  # user is the member of this pg
  pg = ndb.KeyProperty()

  # pg sheet that user requested
  requested_pg = ndb.KeyProperty(repeated=True)
  requested_pg_sheet = ndb.KeyProperty(repeated=True) 

  is_member = ndb.BooleanProperty(default=False)
  added_on = ndb.DateTimeProperty(auto_now_add=True)


def check_id(auth_id, user_id):
  """this function is to get valid user id in condition when user does not 
    login through any openId provider
    
    Args:
      auth_id : openId provider id
      user_id : User provided id
    
    Return:
     user id which needs to set  
  """
  if auth_id:
    return auth_id
  else:
    return user_id

def check_password(password):
  """this is to check for password, if user login through openId then 
  there is no need of password
    
    Args:
      password : user entered password
    
    Return:
     user password 
  """
  if password:
    return password
  else:
    return

def Create_User(auth_id, user_id, name, email, password):
  """Assemble the unique values for a given class and attribute scope.
  Args:
    auth_id : Oauth id of provider
    name : user name
    email : user email
    password : MD5 hash password
  
  Return:
   user :  user instance
  """
  new_user = User.get_or_insert(
      check_id(auth_id, user_id),
      user_id=user_id,
      user_auth_id=auth_id,
      user_name=name,
      user_password=password,
      user_email=email,
  )
  new_user = new_user.put()
  return new_user

def GetUserByEmailId(email):
  """Get User by their email id
  Args:
    email : email id of user
  Return:
    user instance  
  """
  return User.query().filter(User.user_email == email).get()

def GetUserByUserId(user_id):
  """Get User by their user id
  Args:
    user_id : user id of user
  Return:
    user instance  
  """
  return User.query().filter(User.user_id == user_id).get()

def GetActiveUsers():
  """Get all active users
  Return:
    list of user instances  
  """
  return User.query()

def GetActiveUsersIds():
  """ get active users ids """
  return [user.user_id for user in GetActiveUsers()]

def GetActiveUsersEmails():
  """ get active users emails """
  return [user.user_email for user in GetActiveUsers()]

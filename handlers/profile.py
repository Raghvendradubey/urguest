# -*- coding: utf-8 -*-
"imports are going here"
import logging

import webapp2

from google.appengine.ext import ndb

import config
import forms
from lib.base_handler import BaseHandler
from lib.base_handler import sign_up
from lib import utils
from models import pg_ad as ad_model
from models import pg_user as user_model
from models import pg_message
from simpleauth import SimpleAuthHandler


class ProfileHandler(BaseHandler):
  """ user profile """
  def get(self, user_id):
    """ Handles GET /profile """
    user = user_model.GetUserByUserId(user_id)
    if user.user_name:
        page_title = user.user_name
    else:
        page_title = 'profile' 
    params = {
        'page_title': page_title,
        'is_profile': True,
        'user' : user,
       # 'pgs' : pgs
    }
    self.render('profile.html', **params)
    
    
class ProfileQuestion(BaseHandler):
  """ questions asked by user """
  def get(self, user_id):
    """ Handles GET /profile """
    user = user_model.GetUserByUserId(user_id)
    message = pg_message.GetMessageByUser(user.key)
    if user.user_name:
        page_title = user.user_name + ' ' + ' Questions'
    else:
        page_title = 'Questions'     
    params = {
        'page_title': page_title,
        'is_profile_question': True,
        'user' : user,
        'message' : message,
       # 'pgs' : pgs
    }
    self.render('profile.html', **params)
    
class ProfileNotification(BaseHandler):
  """ user notifications """
  def get(self, user_id):
    """ Handles GET /profile """
    user = user_model.GetUserByUserId(user_id)
    message = pg_message.GetMessageByUser(user.key)
    if user.user_name:
        page_title = user.user_name + ' ' + 'Notifications'
    else:
        page_title = 'Notifications'
    params = {
        'page_title': page_title,
        'is_profile_notification': True,
        'user' : user,
        'message' : message,
       # 'pgs' : pgs
    }
    self.render('profile.html', **params)        


class AuthHandler(BaseHandler, SimpleAuthHandler):
  """Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

  # Enable optional OAuth 2.0 CSRF guard
  OAUTH2_CSRF_STATE = True

  USER_ATTRS = {
    'facebook' : {
      'id'     : lambda id: ('avatar_url',
        'http://graph.facebook.com/{0}/picture?type=large'.format(id)),
      'name'   : 'name',
      'email'  : 'email',
      'link'   : 'link'
    },
    'google'   : {
      'picture': 'avatar_url',
      'name'   : 'name',
      'email'  : 'email',
      'profile': 'link'
    },
    'windows_live': {
      'avatar_url': 'avatar_url',
      'name'      : 'name',
      'link'      : 'link'
    },
    'twitter'  : {
      'profile_image_url': 'avatar_url',
      'screen_name'      : 'name',
      'link'             : 'link'
    },
    'linkedin' : {
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'linkedin2' : {
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'foursquare'   : {
      'photo'    : lambda photo: ('avatar_url', photo.get('prefix') + '100x100' + photo.get('suffix')),
      'firstName': 'firstName',
      'lastName' : 'lastName',
      'contact'  : lambda contact: ('email', contact.get('email')),
      'id'       : lambda id: ('link', 'http://foursquare.com/user/{0}'.format(id))
    },
    'openid'   : {
      'id'      : lambda id: ('avatar_url', '/img/missing-avatar.png'),
      'nickname': 'name',
      'email'   : 'link'
    }
  }

  def _on_signin(self, data, auth_info, provider):
    """Callback whenever a new or existing user is logging in.
     data is a user info dictionary.
     auth_info contains access token or oauth token and secret.
    """
    auth_id = '%s:%s' % (provider, data['id'])
    logging.info('Looking for a user with id %s', auth_id)
    user = user_model.User.get_by_id(data['id'])
    _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])
    logging.info(_attrs)

    if user:
      logging.info('Found existing user to log in')
      # Existing users might've changed their profile data so we update our
      # local model anyway. This might result in quite inefficient usage
      # of the Datastore, but we do this anyway for demo purposes.
      #
      # In a real app you could compare _attrs with user's properties fetched
      # from the datastore and update local user in case something's changed.
      user.user_name = _attrs['name']
      user.put()
      self.session['user_id'] = user.key.urlsafe()
      self.local_redirect_to('profile', user_id=user.user_id)

    else:
      # check whether there's a user currently logged in
      # then, create a new user if nobody's signed in,
      # otherwise add this auth_id to currently logged in user.

      if self.logged_in_user('user_id') is not None:
        logging.info('Updating currently logged in user')

        user.user_name = _attrs['name']
        user.put()

      else:
        if _attrs['email']:  
          name = _attrs['name']
          email = _attrs['email']
          auth_id = data['id']
          user = sign_up(self, auth_id, name, email)
          self.local_redirect_to('profile', user_id=user.user_id)
        else:
          self.session['user_name'] = name
          self.session['user_auth_id'] = auth_id    
          self.local_redirect_to('submit_user')

  def logout(self):
    self.session.pop('user_id')
    self.local_redirect_to('home')

  def handle_exception(self, exception, debug):
    logging.error(exception)
    self.abort(404)

  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)

  def _get_consumer_info_for(self, provider):
    """Returns a tuple (key, secret) for auth init requests."""
    return config.AUTH_CONFIG[provider]

  def _to_user_model_attrs(self, data, attrs_map):
    """Get the needed information from the provider dataset."""
    user_attrs = {}
    for k, v in attrs_map.iteritems():
      attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
      user_attrs.setdefault(*attr)

    return user_attrs


class UserSubmit(BaseHandler):
  """Submit the User form on sign up
  Args:
    BaseHandler : Base Class
  """
  def get(self):
    """ get handler method which gets the email and name from session 
    and render step2 signup process
    Render:
     sign_up_step2.html:  sign up step2
    """
    self.form.user_name.data = self.session.get('user_name')
    self.form.user_auth_id.data = self.session.get('user_auth_id')
    params = {
              'sign_up' : True,
              'page_title' : 'SignUp Step 2'
             }
    self.render('signup_step2.html', **params)

  def post(self):
    """ Method to submit sign up form """
    USER_EMAIL_LIST = user_model.GetActiveUsersEmails()
    if self.form.user_email.data in USER_EMAIL_LIST:
        params = {
            'page_title' : 'SignUp',
            'sign_up' : True,
            'sign_up_message' : 'Email Already Exist Please Choose Another One'
        }
        self.render('signup_step2.html', **params)
    else:
      if not self.form.validate():
        return self.get()    
      name = self.form.user_name.data
      email = self.form.user_email.data
      auth_id = self.form.user_auth_id.data
      user = sign_up(self, auth_id, name, email)
      self.session.pop('user_name')
      self.session.pop('user_auth_id')
      self.local_redirect_to('profile', user_id=user.user_id)
    

  @webapp2.cached_property
  def form(self):
    """ It is used to get the SignUpOauth
    Return:
      SignUpOauth: Method of forms
    """
    return forms.SignUpOauth(self)


class ProfileSetting(BaseHandler):
  """ profile setting handler 
  Args:
    BaseHandler : Base class for handler
  """
  def get(self):
    """ method to render setting page """
    if self.logged_in_user('user_id') is None:
      self.abort(404)  
    user_id = self.session.get('user_id')
    user_key = ndb.Key(urlsafe=user_id)
    user = user_key.get()  
    params = {
              'page_title' : 'Profile Setting',
              'is_setting' : True,
              'user' : user
    }
    self.render('profile.html', **params)
      

  def post(self):
    """ method to submit changed setting
    Redirect:
      profile : profile page
    """
    if not self.form.validate():
      return self.get()

    user_id = self.session.get('user_id')
    user_key = ndb.Key(urlsafe=user_id)
    user = user_key.get()
    # submit
    user.user_password = utils.password_hash(self.form.user_password.data)
    user.put()
    self.local_redirect_to('profile', user_id=user.user_id)

  @webapp2.cached_property
  def form(self):
    """It is used to get the SignUpOauth
    Return:
      SignUpOauth: Method of forms
    """
    return forms.PasswordSettingForm(self)


class ProfileDelete(BaseHandler):
  """ delete profile 
  Args:
    BaseHandler : Base class for handler
  """
  def get(self):
    """ method to delete profile
    Redirect:
      profile : profile page
    """
    user_id = self.session.get('user_id')
    user = user_model.User.get_by_id(user_id)
    ads = ad_model.GetUserAds(user.user_id)
    for ad in ads:
      ad.key.delete()
    user.key.delete()
    self.local_redirect_to('profile')

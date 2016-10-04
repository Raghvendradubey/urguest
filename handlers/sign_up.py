
"Imports are going here"
import hashlib
# pylint: disable-msg=F0401
import webapp2
# pylint: enable-msg=F0401
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from lib import utils
from lib.base_handler import BaseHandler
from lib.base_handler import send_message
from lib.base_handler import sign_up
from models import pg_user as user_model
import config
import forms



# pylint: disable-msg=W0311
class SignUpHandler(BaseHandler):
  """It is used as first step of signup, renders html to get email
  of user.
  Args:
    BaseHandler : Base class from lib
  Render:
    sign_up.html : html to get email   
  """

  def get(self):
    """It get the request of sign up process
    Render:
     sign_up.html : html to get email 
    """
    params = {
        'page_title' : 'SignUp',
        'sign_up' : True
    }
    # pylint: disable-msg=W0142
    self.render('sign_up.html', **params)
    
  def post(self):
    """ Method to submit sign up form """
    USER_EMAIL_LIST = user_model.GetActiveUsersEmails()
    if self.form.user_email.data in USER_EMAIL_LIST:
        params = {
            'page_title' : 'SignUp',
            'sign_up' : True,
            'sign_up_message' : 'Email Already Exist Please Choose Another One'
        }
        self.render('sign_up.html', **params)
    else:    
      if not self.form.validate():
        return self.get()

      # not a Oauth login
      auth_id = None
      name = None
      email = self.form.user_email.data
      user = sign_up(self, auth_id, name, email)
      if self.session.get('pg_id') is not None:
        pg_id = self.session.get('pg_id')
        pg = ndb.Key('Pg', pg_id)
        pg = pg.get()
        pg.user = user.key
        pg.put()
        self.session.pop('pg_id')
        taskqueue.add(url='/taskqueue/index-single-pg',
                    queue_name='indexing',
                    params=dict(pg_id=pg.key.urlsafe()))
        self.local_redirect_to('pg_detail', pg_id=pg.key.id())
      else:  
        self.local_redirect_to('profile', user_id=user.user_id)
      # pylint: enable-msg=W0142

  @webapp2.cached_property
  def form(self):
    """It is used to get the SignUpOauth
    Return:
      SignUpOauth: Method of forms
    """
    return forms.SignUpForm(self)


class LoginHandler(BaseHandler):
  """Login Handler
  Args:
    BaseHandler : Base class from lib
  Render:
    sign_up.html : html to get email   
  """

  def get(self):
    """It get the request of login process
    Render:
     sign_up.html : html to get email 
    """
    params = {
        'page_title' : 'Login',
        'login' : True

    }
    # pylint: disable-msg=W0142
    self.render('sign_in.html', **params)
    # pylint: enable-msg=W0142         

  def post(self):
    """It get the request of login process
    Render:
     profile.html : profile html 
    """
    if not self.form.validate():
        return self.get()
    email = self.form.user_email.data
    password = self.form.user_password.data
    password = hashlib.md5("%s" % password).hexdigest()
    user = user_model.GetUserByEmailId(email)
    if user:
      if user.user_email and user.user_password == password:
        self.session['user_id'] = user.key.urlsafe()
        if self.session.get('pg_id') is not None:
          pg_id = self.session.get('pg_id')
          pg = ndb.Key('Pg', pg_id)
          pg = pg.get()
          pg.user = user.key
          pg.put()
          self.session.pop('pg_id')
          taskqueue.add(url='/taskqueue/index-single-pg',
                       queue_name='indexing',
                       params=dict(pg_id=pg.key.urlsafe()))
          self.local_redirect_to('pg_detail', pg_id=pg.key.id())  
        else:  
          self.local_redirect_to('profile', user_id=user.user_id)
      else:
        params = {            
            'page_title' : 'Login',
            'is_login' : True,
            'NotAuthorised' : True,
        }
        # pylint: disable-msg=W0142
        self.render('sign_in.html', **params)
        # pylint: enable-msg=W0142
    else:
      params = {
            'page_title' : 'Login',
            'is_login' : True,
            'NotExist' : True,
      }
      # pylint: disable-msg=W0142
      self.render('sign_in.html', **params)

  @webapp2.cached_property
  def form(self):
    """It is used to get the LoginForm
    Return:
      LoginForm: Method of forms
    """
    return forms.LoginForm(self)


class PasswordHandler(BaseHandler):
  """Login Handler
  Args:
    BaseHandler : Base class from lib
  Render:
    sign_up.html : html to get email   
  """

  def get(self):
    """It get the request of login process
    Render:
     sign_up.html : html to get email 
    """
    params = {
        'page_title' : 'Enter Your Email',
        'forgot_pwd' : True

    }
    # pylint: disable-msg=W0142
    self.render('forgot_pwd.html', **params)
    # pylint: enable-msg=W0142         

  def post(self):
    """It get the request of login process
    Render:
     profile.html : profile html 
    """
    if not self.form.validate():
      return self.get()
    email = self.form.user_email.data
    user = user_model.GetUserByEmailId(email)
    if user:
      password = utils.random_string(config.RANDOM_STRING_SIZE)
      password_hash = utils.password_hash(password)
      user.user_password = password_hash
      user.put()
      send_message(config.SENDER, config.FORGOT_PWD_SUBJECT, 
                   config.FORGOT_PWD_MSG(password), email)
      
      params = {
        'page_title' : 'Enter Your Email',
        'forgot_pwd' : True,
        'message' : config.FORGOT_PWD_MESSAGE

      }
      # pylint: disable-msg=W0142
      self.render('thank_you.html', **params)
    else:
        self.abort(404)  
    
  @webapp2.cached_property
  def form(self):
    """
    Return:
      EmailForm: Method of forms
    """
    return forms.EmailForm(self)    
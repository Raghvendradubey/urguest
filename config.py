#!/usr/bin/python

import os
import re


ON_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')

if ON_DEV:
  ROOT_URL = 'http://localhost:8080'
else:
  #ROOT_URL = 'http://www.urguest.com'
  ROOT_URL = 'http://www.tagfry.com'

SESSION_KEY = "a very long and secret session key goes here"

#USER_APP_MAIL_ID = "@sharedhos.appspotmail.com"
USER_APP_MAIL_ID = "@tagfry3.appspotmail.com"

#PG_SUPPORT_MAIL = 'mukesh.jaiswal@urguest.com'
PG_SUPPORT_MAIL = 'mukesh.jaiswal@tagfry.com'

#APP_MAIL = "support@sharedhos.appspotmail.com"
APP_MAIL = "support@tagfry3.appspotmail.com"

FORGOT_PWD_MESSAGE = "Soon You Will Get New Password From Us Through Email"

THREE_SHARING = 3
TWO_SHARING = 2

SHARING_TYPES = [
                 ('2', '2 Sharing BedRoom'),
                 ('3', '3 Sharing BedRoom')
                 ]

PG_TYPES = {
            '1': 'MALE',
            '2': 'FEMALE'
           }

PG_TYPES_MODEL = {
            1: 'MALE',
            2: 'FEMALE'
           }

SHARING = {  
            TWO_SHARING : '2 Sharing',
            THREE_SHARING : '3 Sharing'
          }                 

webapp2_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': []
  }
}

webapp2_config['webapp2_extras.jinja2'] = {
    'template_path': 'templates',
    'environment_args': {'extensions': ['jinja2.ext.i18n']},
}

error_templates = {
    404: 'errors/404.html',
    500: 'errors/500.html',
}

CITY = "GHAZIABAD"

RANDOM_STRING_SIZE = 3

RANDOM_IMAGE_NAME_SIZE = 9

RANDOM_USER_MAIL_STRING_SIZE = 6

# minimum file size in bytes to upload
MIN_FILE_SIZE = 1

# maximum file size in bytes
MAX_FILE_SIZE = 5000000

IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')

ACCEPT_FILE_TYPES = IMAGE_TYPES

# max width / height
THUMBNAIL_MODIFICATOR = '=s80'

# seconds
EXPIRATION_TIME = 300

SENDER = "Ask Support <admin@sharedhos.appspotmail.com>"

PG_REQUEST_SUBJECT = "Pg Allotment Request"

SUBJECT = "Please Approve you Account"

PG_REQUEST_MESSAGE = lambda email, sharing, url : """ %s is Looking for Allotment of Pg 
                                                   = %s which is %s sharing """ % \
                                                   (email, url, sharing)

FORGOT_PWD_SUBJECT = "New Password for UrGuest"

FORGOT_PWD_MSG = lambda pwd: '%s your password is' % pwd

def Message(email, password, url):
  """Message For Account Approval
  Args:
    email : user email
    password : User Password
    url : url which needs to send for approval
  """
  html = """<html><head></head><body>
            Dear %s:
            Your Current Password is %s
            Please click the below link to activate your Account.
            %s
            Please let us know if you have any questions.

            The ask.com Team
            </body></html>""" % (email, password, url)
  return html

# Google APIs localhost
GOOGLE_APP_ID = '297983716233-4cm4fe1mqr50321haurhvqgbacrh9fj4.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'sq22n-15DdQw1UOLSJ_fAhxb'

# Facebook auth apis
FACEBOOK_APP_ID = '469900009848893'
FACEBOOK_APP_SECRET = '8b7227ec9fb3051cc0ea073548b10495'

"""GOOGLE_APP_ID = '717222205605-r9rj2o9idqhbu5i6g52hps6cv8bi09kf.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'hj3LoBJTeDfHMg9rd4hhAosS'

# Facebook auth apis
FACEBOOK_APP_ID = '233880776753014'
FACEBOOK_APP_SECRET = '9145df68f243525b296feda498edb388'"""


# Key/secret for both LinkedIn OAuth 1.0a and OAuth 2.0
# https://www.linkedin.com/secure/developer
LINKEDIN_KEY = 'consumer key'
LINKEDIN_SECRET = 'consumer secret'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = 'client id'
WL_CLIENT_SECRET = 'client secret'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'oauth1.0a consumer key'
TWITTER_CONSUMER_SECRET = 'oauth1.0a consumer secret'

# https://foursquare.com/developers/apps
FOURSQUARE_CLIENT_ID = 'client id'
FOURSQUARE_CLIENT_SECRET = 'client secret'

# t_config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.email'),
  'linkedin2'   : (LINKEDIN_KEY, LINKEDIN_SECRET,
                  'r_basicprofile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'email'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),
  'foursquare'  : (FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
                  'authorization_code'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_KEY, LINKEDIN_SECRET),

  # OpenID doesn't need any key/secret
}

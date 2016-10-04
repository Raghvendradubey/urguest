# -*- coding: utf-8 -*-
" Imports are going here "
# pylint: disable-msg=F0401
from wtforms import fields
from wtforms import Form
from wtforms import validators
# pylint: enable-msg=F0401

import config
import logging
from models import pg_user as user_models
from models import pg_location as location_model

# intended to stop maliciously long input
FIELD_MAXLENGTH = 200

DESCRIPTION_MAXLENGTH = 300

USER_ID_LIST = user_models.GetActiveUsersIds()

USER_EMAIL_LIST = user_models.GetActiveUsersEmails()

SHARING = [
    (key, value) for key, value in config.SHARING_TYPES
]
     
SHARING.insert(0, ('', 'You Wish To Share'))

PG_TYPE = [
    (key, value) for key, value in config.PG_TYPES.items()
]

PG_TYPE.insert(0, ('', 'Choose PG Type'))

SHARING_THREE_SHEET = [(str(i), str(i)) for i in range(10)]
     
SHARING_THREE_SHEET.insert(0, ('', 'Number of 3 sharing sheets'))

SHARING_TWO_SHEET = [(str(i), str(i)) for i in range(10)]
     
SHARING_TWO_SHEET.insert(0, ('', 'Number of 2 sharing sheets'))

LOCATION = [
      ((location.city_name).lower(), (location.city_name))
      for location in location_model.GetCities()
    ]


# custom validator
def sharing_type_check(form, field):
  if int(field.data) not in range(10):
    logging.info("field data is %s", field.data)
    raise validators.ValidationError('Wrong Type. Please select one from the dropdown menu.')

def check_user_id(form, field):
  if field.data in USER_ID_LIST:
    raise validators.ValidationError('User Id already exist please choose another one')

def check_user_email(form, field):
  if field.data in USER_EMAIL_LIST:
    raise validators.ValidationError('Email Id already exist please choose another one')

def check_user_email_forgot_pwd(form, field):
  if field.data not in USER_EMAIL_LIST:
    logging.info('USER EMAIL LIST %s' %  USER_EMAIL_LIST)  
    raise validators.ValidationError('User Does not Exist')

def location_type_check(form, field):
  if field.data not in LOCATION:
    raise validators.ValidationError('Wrong  lOCATION. Please select one from the dropdown menu.')

def location_check(form, field):
  if (field.data).lower() in LOCATION:
    raise validators.ValidationError('Wrong  lOCATION. It is already exist.')


# pylint: disable-msg=W0311
# pylint: disable-msg=R0903
# Base Form Classes
class BaseForm(Form):
  """ Base Form class for all the Form classes, it overrides the Form 
  request handler __init__ method.
  Argument:
    Form : wtform's Form
  """
  def __init__(self, request_handler):
    """ Constructor class of BaseForm overrides __init__ method of Form
    Argument:
      request_handler : request handler variable
    """
    # pylint: disable-msg=E1002
    super(BaseForm, self).__init__(request_handler.request.POST)
    # pylint: enable-msg=E1002


# Custom Form Classes
class AddLocationForm(BaseForm):
  """ Add category Form
  Argument:
    BaseForm : Base form class  
  """
  location = fields.TextField('', [
      validators.Required(),
      location_check,
  ])
  
  
class EmailForm(BaseForm):
  """ Email Form
  Argument:
    BaseForm : Base form class  
  """
  user_email = fields.TextField('', [
      validators.Required(),
      validators.Email(),
      check_user_email_forgot_pwd
  ])


class LoginForm(BaseForm):
  """ Login Form
  Argument:
    BaseForm : Base form class  
  """
  user_email = fields.TextField('', [
      validators.Required(),
      validators.Email()
  ])
  user_password = fields.TextField('', [
      validators.Required(),
  ])
  login_check = fields.BooleanField('Keep me logged in')


class SignUpForm(BaseForm):
  """ Sign up Form
  Argument:
    BaseForm : Base form class  
  """
  user_email = fields.TextField('', [
      validators.Required(),
      validators.Email()
  ])
  agree_with_terms = fields.BooleanField(('Agree to our terms'), [
      validators.Required(),
  ])


class PasswordSettingForm(BaseForm):
  """ Password setting  Form
  Argument:
    BaseForm : Base form class  
  """
  user_password = fields.TextField(('Enter New Password'), [
      validators.Required(),
      validators.EqualTo('user_password_confirm', message='Password must match.')
  ])
  user_password_confirm = fields.TextField(('Confirm New Password'), [
      validators.Required(),
  ])


class SignUpOauth(BaseForm):
  """ It is used to get the email of the user in sign up process
  Argument:
    BaseForm : Base form class
  Attribute:
    user_email : It defines the email address of the user  
  """
  user_email = fields.TextField(('Email Address'), [
      validators.Required(),
      check_user_email,
      validators.Email(),
      validators.EqualTo('user_email_confirm', message='Email addresses must match.')
  ])
  user_email_confirm = fields.TextField(('Repeat Email Address'), [
      validators.Required(),
      validators.Email(),
  ])
  # Hidden Fields
  user_name = fields.HiddenField([
      validators.Required()
  ])
  user_auth_id = fields.HiddenField([
      validators.Required(),
  ])
  user_avatar = fields.HiddenField([
      validators.Required(),
      validators.URL(require_tld=True)
  ])


class AdPostForm(BaseForm):
  """ ad form  """
  location = fields.SelectField('', [
      validators.Required(),
  ], coerce=str)

  title = fields.TextField('', [
      validators.Required(),
  ])
  price = fields.DecimalField('', [
      validators.Required(),
  ])

  description = fields.TextAreaField('', [
      validators.Required(),
  ])

  street_address = fields.TextField('', [
      validators.Required(),
  ])
  
  sharing_three = fields.SelectField('', [
    # need to do this section
      validators.Required(),
   #   sharing_type_check
  ],coerce=str, choices=SHARING_THREE_SHEET)
  
  sharing_two = fields.SelectField('', [
     validators.Required(),
     # sharing_type_check
  ],coerce=str,choices=SHARING_TWO_SHEET)
  
  pg_type = fields.SelectField('', [
     validators.Required(),
     # sharing_type_check
  ],coerce=str,choices=PG_TYPE)
  
  


class CategoryForm(BaseForm):
  """ Category Form
  Argument:
    BaseForm : Base form class  
  """
  category_name = fields.TextField(('Suggest category'), [
      validators.Required()
  ])

class UserMessageForm(BaseForm):
  """ User Message
  Argument:
    BaseForm : Base form class  
  """
  description = fields.TextAreaField('', [
      validators.Required(),
  ])
  
  is_message = fields.HiddenField([
      validators.Required(),
  ])

class BookPgForm(BaseForm):
  """ Book Pg form  """
  user_email = fields.TextField('', [
      validators.Required(),
      validators.Email(),
  ])
  sharing = fields.SelectField('', [
      validators.Required(),
  ], coerce=str)
# pylint: enable-msg=R0903

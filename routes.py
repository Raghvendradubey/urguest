#!/usr/bin/python

"Imports are going here"
# pylint: disable-msg=F0401
from webapp2_extras import routes
# pylint: enable-msg=F0401

from handlers import about_us
from handlers import admin
from handlers import contact
from handlers import create_bucket
from handlers import faq
from handlers import file_upload
from handlers import home
from handlers import pg_ad
from handlers import profile
from handlers import property_owner
from handlers import pg_location
from handlers import search
from handlers import sign_up

# pylint: disable-msg=C0103
secure_scheme = 'https'
# pylint: enable-msg=C0103

# pylint: disable-msg=W0311
# ROUTES Dictionary
ROUTES = {

    'home': dict(
        handler=home.HomeHandler,
        url='/'
    ),
          
    'about_us': dict(
        handler=about_us.AboutUsHandler,
        url='/about-us'
    ), 
          
    'contact_us': dict(
        handler=contact.ContactHandler,
        url='/contact-us'
    ),  
          
    'faq': dict(
        handler=faq.FaqHandler,
        url='/faq'
    ),  
          
    'owner': dict(
        handler=property_owner.OwnerHandler,
        url='/owner'
    ),        
          
    'search_pg': dict(
        handler=search.PgSearchHandler,
        url='/search'
    ),                  
             
    'admin': dict(
        redirect_to_name='home',
        url='/admin'
    ),

    'import_csv': dict(
        handler=admin.CsvImporter,
        strict_slash=True,
        url='/admin/add-test-data'
    ),
          
    'sign_up': dict(
        handler=sign_up.SignUpHandler,
        url='/sign-up'
    ),

    'login': dict(
        handler=sign_up.LoginHandler,
        url='/login'
    ),
          
    'fpwd': dict(
        handler=sign_up.PasswordHandler,
        url='/fpwd'
    ),  
          
    'change_pwd': dict(
        handler=profile.ProfileSetting,
        url='/change-pwd'
    ),           

    'logout': dict(
        handler=profile.AuthHandler,
        handler_method='logout',
        strict_slash=True,
        url='/logout'
    ),    

    'auth_login': dict(
        handler=profile.AuthHandler,
        handler_method='_simple_auth',
        strict_slash=True,
        url='/auth/<provider>'
    ),

    'auth_callback': dict(
        handler=profile.AuthHandler,
        handler_method='_auth_callback',
        strict_slash=True,
        url='/auth/<provider>/callback'
    ),

    'profile': dict(
        handler=profile.ProfileHandler,
        strict_slash=True,
        url='/p/<user_id>'
    ),
          
    'questions': dict(
        handler=profile.ProfileQuestion,
        strict_slash=True,
        url='/p/question/<user_id>'
    ),    
          
    'notification': dict(
        handler=profile.ProfileNotification,
        strict_slash=True,
        url='/p/notification/<user_id>'
    ),         

    'submit_user': dict(
        handler=profile.UserSubmit,
        strict_slash=True,
        url='/submit_user'
    ),

    'add_location': dict(
        handler=pg_location.LocationSubmit,
        strict_slash=True,
        url='/add-location'
    ),
          
    'create_bucket': dict(
        handler=create_bucket.MainPage,
        strict_slash=True,
        url='/admin/create-bucket'
    ),        

    'pg_post': dict(
        handler=pg_ad.PgPost,
        strict_slash=True,
        url='/pg-post'
    ),

    'setting': dict(
        handler=profile.ProfileSetting,
        url='/setting'
    ),
          
    'taskqueue_add_data': dict(
        handler=admin.CsvAddTask,
        url='/taskqueue/add-data'
    ),      
              
    'taskqueue_index_single_city': dict(
        handler=search.IndexSingleCityHandler,
        url='/taskqueue/index-single-city'
    ),
          
    'taskqueue_index_pg': dict(
        handler=search.IndexSinglePgHandler,
        url='/taskqueue/index-single-pg'
    ),
          
    'taskqueue_delete_index': dict(
        handler=search.DeleteIndex,
        url='/taskqueue/delete-index'
    ),      

    'pg_detail': dict(
        handler=pg_ad.PgDetail,
        strict_slash=True,
        url='/pg/<pg_id>'
    ),

    'pg_edit': dict(
        handler=pg_ad.PgEdit,
        strict_slash=True,
        url='/pg-edit/<pg_id>'
    ),
          
    'pg_delete': dict(
        handler=pg_ad.PgDelete,
        strict_slash=True,
        url='/pg-delete/<pg_id>'
    ),      
          
    'pg_request_user': dict(
        handler=pg_ad.PgRequestUser,
        strict_slash=True,
        url='/request-user/<pg_id>'
    ),      

    # /uplaod is initialized in app.js also
    'upload': dict(
        handler=file_upload.UploadHandler,
        url='/upload'
    ),
          
    'upload_edit': dict(
        handler=file_upload.UploadEditHandler,
        url='/upload-edit/<pg_id>'
    ),      

    'download': dict(
        handler=file_upload.DownloadHandler,
        url='/(.+)/([^/]+)/([^/]+)'
    ),            
}


def add_routes(app):
  """ add routes to the app
  
  Args:
    app : instance of the application
  """
  for name, value_dict in ROUTES.iteritems():
    handler_method = value_dict.get('handler_method', None)
    url = value_dict.get('url')
    app.router.add(routes.RedirectRoute(
        url, name=name, handler=value_dict.get('handler'),
        handler_method=handler_method, strict_slash=True,
        redirect_to_name=value_dict.get('redirect_to_name')))

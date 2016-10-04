from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import logging

from lib.base_handler import send_message
from models import pg_message
from models import pg_user

import config

class LogSenderHandler(InboundMailHandler):

    def receive(self, mail_message):
        if mail_message.to == config.APP_MAIL:
            user = pg_user.GetUserByEmailId(mail_message.sender)
            html_bodies = mail_message.bodies('text/html')
            for content_type, body in html_bodies:
              decoded_html = body.decode()
            pg_message.AddNewMessage(user.key, user.pg, member_message=None, decoded_html)
        else:    
          user = pg_user.GetUserByEmailId(mail_message.sender)
          html_bodies = mail_message.bodies('text/html')
          for content_type, body in html_bodies:
            decoded_html = body.decode()
            pg_message.AddNewMessage(user.key, user.pg, decoded_html, message=None)
        send_message(mail_message.sender, mail_message.subject,
                     decoded_html, mail_message.to)


app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = 'ravidubey009@gmail.com (Raghvendra Dubey)'

import os, sys
# Third party libraries path must be fixed before importing webapp2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib/vendor'))

import webapp2

import config
import routes

from lib.base_handler import handle_error


app = webapp2.WSGIApplication(debug=config.ON_DEV,
                              config=config.webapp2_config)

app.error_handlers[404] = handle_error
if not app.debug:
    app.error_handlers[500] = handle_error
routes.add_routes(app)

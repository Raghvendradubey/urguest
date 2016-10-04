# -*- coding: utf-8 -*-
#!/usr/bin/python

"Imports are going here"
import csv
import glob

# pylint: disable-msg=F0401
# pylint: disable-msg=E0611
from google.appengine.api import taskqueue
# pylint: enable-msg=E0611
# pylint: enable-msg=F0401

# pylint: disable-msg=F0401
from lib.base_handler import BaseHandler
from lib import utils
from models import pg_location as location_model
# pylint: enable-msg=F0401


# pylint: disable-msg=W0311
# pylint: disable-msg=E1101
class CsvImporter(BaseHandler):
  """ Add categories and ad data in datastore using csv file. """
  def get(self):
    """ get csv file and upload data to datastore """
    user_csv_file = glob.glob('testdata/upload.csv')
    for csv_file in user_csv_file:
      csv_file = open(csv_file, "rb")
      reader = csv.reader(csv_file, delimiter=',')
      rownum = 0
      for row in reader:
        if rownum == 0:
          header = row
        else:
          colnum = 0
          csv_dict = dict()
          for col in row:
            csv_dict[header[colnum]] = col
            colnum += 1
          # PLEASE READ #
          # saving a new data to datastore
          taskqueue.add(url='/taskqueue/add-data',
                  queue_name='add-data',
                  params=dict(city=csv_dict['City']))
        rownum += 1
      self.response.out.write("data successfully created")


class CsvAddTask(BaseHandler):
  """ Adding data to datastore through task add """
  def post(self):
    """handler method gets the taskqueue request from CsvImporter class
    and add data to datastore 
    """
    city = self.request.get('city')
    city = location_model.AddCity(city)

    # index ad for search
    taskqueue.add(url='/taskqueue/index-single-city',
                  queue_name='indexing',
                  params=dict(city_id=city.urlsafe()))
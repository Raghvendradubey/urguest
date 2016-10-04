# -*- coding: utf-8 -*-
import logging

import webapp2
from google.appengine.api import search
from google.appengine.ext import ndb
from lib import utils
from lib.base_handler import BaseHandler
from models import pg_ad as pg_model
from models import pg_location as location_model


PG_INDEX = 'pg_index'
CITY_INDEX = 'city_index'
INDEX_BATCH_SIZE = 100
MAX_PG_SEARCH_RESULTS = 10


class DeleteIndex(webapp2.RequestHandler):
  """It deletes index
  Args:
    webapp2.RequestHandler : Request Handler class
  """
  def post(self):
    delete_single_index(index=self.request.get('index'), document_id=self.request.get('document_id'))


def delete_single_index(index, document_id):
  """It delete index of page, category or link
  Args:
    index : index of page or category or link which we want to delete
    document_id : id which we want to delete
  """
  doc_index = search.Index(name=index)
  doc_index.delete(document_id)

class IndexPgsHandler(webapp2.RequestHandler):
  """Rebuilds index for events."""
  def get(self):
    logging.info('Deleting event index...')
    doc_index = search.Index(name=PG_INDEX)
    while True:
      document_ids = [document.doc_id
                      for document in doc_index.get_range(ids_only=True)]
      if not document_ids:
        break
      doc_index.delete(document_ids)
    logging.info('Deleted everything...')
    IndexPgs()


class IndexSinglePgHandler(webapp2.RequestHandler):
  """Rebuilds index entry for single event"""
  def post(self):
    IndexPgs(pg_id=self.request.get('pg_id'))
    

def IndexPgs(pg_id=None):
  if pg_id:
    # e.g. if event is edited, modified, newly added...
    logging.info('Indexing pg %s...', pg_id)
    pg_id = ndb.Key(urlsafe=pg_id)
    pgs = [pg_id.get()]
  else:
    logging.info('Rebuilding search index for all pgs...')
    pgs = pg_model.GetPgs()

  docs = []
  for pg in pgs:
    logging.info('Preparing index entry for pg %s...' % pg.pg_title)
    search_fields = []
    
    search_fields.append(search.TextField(name='pg_title',
                                          value=pg.pg_title))
    search_fields.append(search.TextField(name='pg_detail',
                                          value=pg.pg_detail))
    search_fields.append(search.TextField(name='pg_price',
                                          value=str(pg.pg_price)))
    search_fields.append(search.TextField(name='street_address',
                                          value=str(pg.pg_street_address)))

    document = search.Document(doc_id=pg.key.urlsafe(),
                               fields=search_fields)
    docs.append(document)

  # adding to index
  logging.info('Indexing...')
  for pg_docs in utils.chunks(docs, INDEX_BATCH_SIZE):
    search.Index(name=PG_INDEX).put(pg_docs)


class IndexSingleCityHandler(webapp2.RequestHandler):
  """Rebuilds index entry for single event"""
  def post(self):
    IndexCity(city_id=self.request.get('city_id'))


def IndexCity(city_id=None):
  if city_id:
    # e.g. if event is edited, modified, newly added...
    logging.info('Indexing city %s...', city_id)
    city_id = ndb.Key(urlsafe=city_id)
    cities = [city_id.get()]
  else:
    logging.info('Rebuilding search index for all cities...')
    cities = location_model.GetCities()

  docs = []
  for city in cities:
    logging.info('Preparing index entry for city %s...' % city.city_name)
    search_fields = []
    search_fields.append(search.TextField(name='city_name',
                                          value=city.city_name))

    document = search.Document(doc_id=city.key.urlsafe(),
                               fields=search_fields)
    docs.append(document)

  # adding to index
  logging.info('Indexing...')
  for city_docs in utils.chunks(docs, INDEX_BATCH_SIZE):
    search.Index(name=CITY_INDEX).put(city_docs)


class PgSearchHandler(BaseHandler):
  def get(self):
    request_values = self.request.GET
    query_string = request_values.get('q', '')
    logging.info(query_string)
    public_query = request_values.get('q', '')
    next_cursor_urlsafe = request_values.get('c', None)
    if next_cursor_urlsafe == None:
      cursor = search.Cursor()
    else:
      cursor = search.Cursor(web_safe_string=next_cursor_urlsafe)

    ad_keys = []
    # TODO(someone): how to order? or no order?
    options = search.QueryOptions(limit=MAX_PG_SEARCH_RESULTS,
                                  ids_only=True,
                                  cursor=cursor)
    query = search.Query(query_string=query_string, options=options)

    index = search.Index(name=PG_INDEX)
    logging.info(query)
    results = index.search(query)
    for result in results:
      logging.info(result.doc_id)
      ad_keys.append(ndb.Key(urlsafe=result.doc_id))
    ads = ndb.get_multi(ad_keys)

    next_cursor = results.cursor
    next_cursor_urlsafe = None
    if next_cursor:
      next_cursor_urlsafe = next_cursor.web_safe_string

    has_next_page = False
    if (len(ads) == MAX_PG_SEARCH_RESULTS and
        results.number_found > MAX_PG_SEARCH_RESULTS):
      has_next_page = True
    ask_user = self.logged_in_user('user_id')
    for ad in ads:
        logging.info(ad.pg_title)
    params = {
        'page_title': 'Ask search',
        'is_pg_search': True,
        'ask_user' : ask_user,
        'pgs': ads,
        'cursor': next_cursor_urlsafe,
        'query': public_query,
        'has_next_page': has_next_page,
        'result_count': results.number_found,
        'robots_meta': 'noindex, follow',
    }
    self.render('home_page.html', **params)

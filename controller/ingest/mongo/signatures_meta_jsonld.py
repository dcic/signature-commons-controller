import os
import pymongo
import json
from ...util import first, mongo_bulk_upsert

inputs = (
  '*.signatures.jsonld',
)

def requirements(uri=[], **kwargs):
  return 'mongo' in set([u.scheme for u in uri])

def ingest(input_files, uri=[], limit=1000, **kawrgs):
  input_file, = input_files
  # Get mongo uri
  mongo_uri = first(u for u in uri if 'mongo' in u.scheme.split('+'))
  # Get extract mongo db name
  db = mongo_uri.path[1:]
  del mongo_uri.path
  # Instantiate mongo client
  mongo = pymongo.MongoClient(str(mongo_uri))
  # Get mongo db
  db = getattr(mongo, mongo_uri.path[1:])
  #
  def generate_signatures():
    with open(input_file, 'r') as fr:
      for signature in map(json.loads, fr):
        yield {
          '_id': signature['@id'],
        }, {
          '$set': {
            'library': signature['library'],
            'meta': signature['meta'],
          },
        }
  #
  mongo_bulk_upsert(
    db.signature_meta,
    generate_signatures(),
    limit=limit,
  )

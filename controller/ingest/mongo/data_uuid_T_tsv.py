import os
import pymongo
import csv
from ...util import first, mongo_bulk_upsert

inputs = (
  '*.data.uuid.T.tsv',
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
      reader = csv.reader(fr, delimiter='\t')
      entities = next(iter(reader))[1:]
      #
      for line in reader:
        sigid = line[0]
        yield {
          '_id': sigid,
        }, {
          '$set': {
            'data.expression': {
              entid: float(expression)
              for entid, expression in zip(entities, line[1:])
            },
          },
        }
  #
  mongo_bulk_upsert(
    db.signature_data,
    generate_signatures(),
    limit=limit,
  )

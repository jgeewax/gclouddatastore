import json
import os.path

import gclouddatastore


DATASET_ID = 'jgatsby-storage'
CLIENT_EMAIL = '29903432081-2qogb45k5olu0j3b7rebktohkm2ncv2b@developer.gserviceaccount.com'
PRIVATE_KEY_PATH = os.path.dirname(__file__) + '/jgatsby-storage.key'


def main():
  connection = gclouddatastore.get_connection(
      DATASET_ID, CLIENT_EMAIL, PRIVATE_KEY_PATH)
  query = connection.query('Thing').limit(2)
  results = query.fetch()
  print json.dumps(results, indent=2)


if __name__ == '__main__':
  main()

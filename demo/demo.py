import json
import os.path

import gclouddatastore


DATASET_ID = 'jgatsby-storage'
CLIENT_EMAIL = '29903432081-2qogb45k5olu0j3b7rebktohkm2ncv2b@developer.gserviceaccount.com'
PRIVATE_KEY_PATH = os.path.dirname(__file__) + '/jgatsby-storage.key'


def main():
  # Establish a connection to use for querying.
  connection = gclouddatastore.get_connection(
      DATASET_ID, CLIENT_EMAIL, PRIVATE_KEY_PATH)

  # Start with a Query for Things.
  query = connection.query().kind('Thing')

  # Show us 2 of them.
  print query.limit(2).fetch()

  # Show us Things in another namespace.
  print query.namespace('other-namespace').fetch()

  # Show us Things named Computer.
  print query.filter('name =', 'Computer').fetch()

  # Show us things named Computer with extra filters.
  print query.filter('name =', 'Computer').filter(
      'my_int_value =', 1234).fetch()


if __name__ == '__main__':
  main()

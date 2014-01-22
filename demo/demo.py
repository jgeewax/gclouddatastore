import os.path

import gclouddatastore
from gclouddatastore.key import Key


DATASET_ID = 'jgatsby-storage'
CLIENT_EMAIL = '29903432081-2qogb45k5olu0j3b7rebktohkm2ncv2b@developer.gserviceaccount.com'
PRIVATE_KEY_PATH = os.path.dirname(__file__) + '/jgatsby-storage.key'


def main():
  # Establish a connection to use for querying.
  connection = gclouddatastore.get_connection(CLIENT_EMAIL, PRIVATE_KEY_PATH)
  dataset = connection.dataset('jgatsby-storage')

  print '\nCreating a new Thing called Toy...'
  toy = dataset.entity('Thing')
  toy.update({'name': 'Toy', 'some_int_value': 1234})
  toy.save()

  print '\nLooking up the Toy...'
  print dataset.get_entities([toy.key()])

  print '\nDeleting the Toy...'
  toy.delete()

  print '\nLooking up the Toy again (this should be empty)...'
  print dataset.get_entities([toy.key()])

  query = dataset.query().kind('Thing')

  print '\nShowing first 2 Things...'
  print query.limit(2).fetch()

  print '\nShowing Things named Computer...'
  print query.filter('name =', 'Computer').fetch()

  print '\nFilter by multiple things...'
  print query.filter('name =', 'Computer').filter(
      'my_int_value =', 1234).fetch()


if __name__ == '__main__':
  main()

import copy

from protobuf_to_dict import protobuf_to_dict

from gclouddatastore import datastore_v1_pb2 as datastore_pb


class Query(object):

  def __init__(self, *kinds):
    self.connection = None
    self.query = datastore_pb.Query()

    for kind in kinds:
      self.query.kind.add().name = kind

  def _clone(self):
    # TODO(jjg): Double check that this makes sense...
    clone = copy.deepcopy(self)
    clone.connection = self.connection  # Shallow copy the connection.
    return clone

  def fetch(self, connection=None):
    connection = connection or self.connection
    if not connection:
      raise ValueError

    response = connection._run_query(self.query)
    return [protobuf_to_dict(e.entity) for e in response.batch.entity_result]

  def filter(self, prop, value):
    clone = self._clone()
    # clone.query.do_something_with_filters()....
    return clone

  def limit(self, limit):
    clone = self._clone()
    clone.query.limit = limit
    return clone

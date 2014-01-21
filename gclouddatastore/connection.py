import httplib2
import json

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore import helpers
from gclouddatastore.dataset import Dataset
from gclouddatastore.entity import Entity
from gclouddatastore.key import Key
from gclouddatastore.query import Query


class Connection(object):

  """
  A connection Google Cloud Datastore via the Protobuf API.

  This class should understand only the basic types (and protobufs)
  in method arguments, however should be capable of returning advanced types.
  """

  API_BASE_URL = 'https://www.googleapis.com'
  API_VERSION = 'v1beta2'

  def __init__(self, credentials=None):
    self._credentials = credentials
    self._http = None

  @property
  def http(self):
    if not self._http:
      self._http = httplib2.Http()
      if self._credentials:
        self._http = self._credentials.authorize(self._http)
    return self._http

  def _request(self, dataset_id, method, data):
    headers = {
        'Content-Type': 'application/x-protobuf',
        'Content-Length': str(len(data)),
        }
    headers, content = self.http.request(
        uri=self.build_api_url(dataset_id=dataset_id, method=method),
        method='POST', headers=headers, body=data)

    if headers['status'] != '200':
      raise Exception('Request failed. Error was: %s' % content)

    return content

  def _rpc(self, dataset_id, method, request_pb, response_pb_cls):
    response = self._request(dataset_id=dataset_id, method=method,
                             data=request_pb.SerializeToString())
    return response_pb_cls.FromString(response)

  def build_api_url(self, dataset_id, method, base_url=None, api_version=None):
    template = (
        '{api_base}'
        '/datastore/{api_version}'
        '/datasets/{dataset_id}'
        '/{method}')

    return template.format(api_base=(base_url or self.API_BASE_URL),
                           api_version=(api_version or self.API_VERSION),
                           dataset_id=dataset_id, method=method)

  def dataset(self, *args, **kwargs):
    """
    Factory method for Dataset objects.
    """
    kwargs['connection'] = self
    return Dataset(*args, **kwargs)

  def run_query(self, dataset_id, query_pb, namespace=None):
    request = datastore_pb.RunQueryRequest()

    if namespace:
      request.partition_id.namespace = namespace

    request.query.CopyFrom(query_pb)
    response = self._rpc(dataset_id, 'runQuery', request, datastore_pb.RunQueryResponse)
    return [Entity.from_protobuf(e.entity) for e in response.batch.entity_result]

  def get_entities(self, dataset_id, key_pbs):
    lookup_request = datastore_pb.LookupRequest()

    for key_pb in key_pbs:
      lookup_request.key.add().CopyFrom(key_pb)

    lookup_response = self._rpc(dataset_id, 'lookup', lookup_request,
                                datastore_pb.LookupResponse)

    return [Entity.from_protobuf(result.entity)
            for result in lookup_response.found]

  def get_entity(self, dataset_id, key_pb):
    entities = self.get_entities(dataset_id, [key_pb])
    if entities:
      return entities[0]

  def save_entity(self, dataset_id, key_pb, properties):
    # Create a non-transactional commit request.
    commit_request = datastore_pb.CommitRequest()
    commit_request.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL

    # TODO: Make this work with update, etc.
    mutation = commit_request.mutation.insert_auto_id.add()

    # First set the (partial) key.
    mutation.key.CopyFrom(key_pb)

    for name, value in properties.iteritems():
      prop = mutation.property.add()
      # Set the name of the property.
      prop.name = name

      # Set the appropriate value.
      pb_attr, pb_value = helpers.get_protobuf_attribute_and_value(value)
      setattr(prop.value, pb_attr, pb_value)

    response = self._rpc(dataset_id, 'commit', commit_request, datastore_pb.CommitResponse)

    return response.mutation_result.insert_auto_id_key[0]

  def delete_entities(self, dataset_id, key_pbs):
    # Create a non-transactional commit request.
    commit_request = datastore_pb.CommitRequest()
    commit_request.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL

    for key_pb in key_pbs:
      mutation = commit_request.mutation.delete.add()
      mutation.CopyFrom(key_pb)

    return self._rpc(dataset_id, 'commit', commit_request,
                     datastore_pb.CommitResponse)

  def delete_entity(self, dataset_id, key_pb):
    return self.delete_entities(dataset_id, [key_pb])

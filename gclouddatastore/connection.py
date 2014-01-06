import httplib2
import json

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore import helpers
from gclouddatastore.entity import Entity
from gclouddatastore.key import Key
from gclouddatastore.query import Query


class Connection(object):

  API_BASE_URL = 'https://www.googleapis.com'
  API_VERSION = 'v1beta2'

  def __init__(self, dataset_id, credentials=None):
    self._dataset_id = dataset_id
    self._credentials = credentials
    self._http = None

  @property
  def api_url(self):
    return '{api_base}/datastore/{api_version}/datasets/{dataset_id}/'.format(
        api_base=self.API_BASE_URL, api_version=self.API_VERSION,
          dataset_id=self._dataset_id)

  @property
  def http(self):
    if not self._http:
      self._http = httplib2.Http()
      if self._credentials:
        self._http = self._credentials.authorize(self._http)
    return self._http

  def _request(self, method, data):
    headers = {
        'Content-Type': 'application/x-protobuf',
        'Content-Length': str(len(data)),
        }
    headers, content = self.http.request(uri=self.api_url + method,
        method='POST', headers=headers, body=data)

    # TODO(jjg): Check that nothing went wrong.
    if headers['status'] != '200':
      raise Exception('Request failed. Error was: %s' % content)

    return content

  def _rpc(self, method, request_pb, response_pb_cls):
    response = self._request(method=method, data=request_pb.SerializeToString())
    return response_pb_cls.FromString(response)

  def _run_query(self, query, namespace=None):
    request = datastore_pb.RunQueryRequest()

    if namespace:
      request.partition_id.namespace = namespace

    request.query.CopyFrom(query)
    return self._rpc('runQuery', request, datastore_pb.RunQueryResponse)

  def query(self, *args, **kwargs):
    kwargs['connection'] = self
    return Query(*args, **kwargs)

  def get_entities(self, keys):
    lookup_request = datastore_pb.LookupRequest()

    for key in keys:
      if not key.dataset_id():
        key.dataset_id(self._dataset_id)
      lookup_request.key.add().CopyFrom(key.to_protobuf())

    lookup_response = self._rpc(
        'lookup', lookup_request, datastore_pb.LookupResponse)

    return [Entity.from_protobuf(result.entity)
            for result in lookup_response.found]

  def new_entity(self, kind, namespace=None):
    key = Key(dataset_id=self._dataset_id, namespace=namespace,
              path=[{'kind': kind}])
    return Entity(key=key, connection=self)

  def save_entity(self, entity):
    # Create a non-transactional commit request.
    commit_request = datastore_pb.CommitRequest()
    commit_request.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL

    mutation = commit_request.mutation.insert_auto_id.add()

    # First set the (partial) key.
    mutation.key.CopyFrom(entity.key().to_protobuf())

    for name, value in entity.iteritems():
      prop = mutation.property.add()
      # Set the name of the property.
      prop.name = name

      # Set the appropriate value.
      pb_attr, pb_value = helpers.get_protobuf_attribute_and_value(value)
      setattr(prop.value, pb_attr, pb_value)

    response = self._rpc('commit', commit_request, datastore_pb.CommitResponse)

    return response.mutation_result.insert_auto_id_key[0]

  def delete_entities(self, entities):
    # Create a non-transactional commit request.
    commit_request = datastore_pb.CommitRequest()
    commit_request.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL

    for entity in entities:
      mutation = commit_request.mutation.delete.add()
      mutation.CopyFrom(entity.key().to_protobuf())

    return self._rpc('commit', commit_request, datastore_pb.CommitResponse)

  def delete_entity(self, entity):
    return self.delete_entities([entity])

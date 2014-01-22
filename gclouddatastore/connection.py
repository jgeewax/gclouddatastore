import httplib2

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore import helpers
from gclouddatastore.dataset import Dataset


class Connection(object):

  """
  A connection Google Cloud Datastore via the Protobuf API.

  This class should understand only the basic types (and protobufs)
  in method arguments, however should be capable of returning advanced types.
  """

  API_BASE_URL = 'https://www.googleapis.com'
  """The base of the API call URL."""

  API_VERSION = 'v1beta2'
  """The version of the API, used in building the API call's URL."""

  API_URL_TEMPLATE = ('{api_base}/datastore/{api_version}'
                      '/datasets/{dataset_id}/{method}')
  """A template used to craft the URL pointing toward a particular API call."""

  def __init__(self, credentials=None):
    """
    :type credentials: :class:`gclouddatastore.credentials.Credentials`
    :param credentials: The OAuth2 Credentials to use for this connection.
    """
    self._credentials = credentials
    self._http = None

  @property
  def http(self):
    """A getter for the HTTP transport used in talking to the API.

    :returns: `httplib2.Http` object used to transport data.
    """
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

  @classmethod
  def build_api_url(cls, dataset_id, method, base_url=None, api_version=None):
    """Construct the URL for a particular API call.

    :type dataset_id: string
    :param dataset_id: The ID of the dataset to connect to.
                       This is usually your project name in the cloud console.

    :type method: string
    :param method: The API method to call (ie, runQuery, lookup, ...).

    :type base_url: string
    :param base_url: The base URL where the API lives.
                     You shouldn't have to provide this.

    :type api_version: string
    :param api_version: The version of the API to connect to.
                        You shouldn't have to provide this.
    """
    return cls.API_URL_TEMPLATE.format(
        api_base=(base_url or cls.API_BASE_URL),
        api_version=(api_version or cls.API_VERSION),
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
    return [e.entity for e in response.batch.entity_result]

  def lookup(self, dataset_id, key_pbs):
    lookup_request = datastore_pb.LookupRequest()

    single_key = isinstance(key_pbs, datastore_pb.Key)

    if single_key:
      key_pbs = [key_pbs]

    for key_pb in key_pbs:
      lookup_request.key.add().CopyFrom(key_pb)

    lookup_response = self._rpc(dataset_id, 'lookup', lookup_request,
                                datastore_pb.LookupResponse)

    results = [result.entity for result in lookup_response.found]

    if single_key:
      if results:
        return results[0]
      else:
        return None

    return results

  def save_entity(self, dataset_id, key_pb, properties):
    # TODO: Is this the right method name?
    # Create a non-transactional commit request.
    commit_request = datastore_pb.CommitRequest()
    commit_request.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL

    # TODO: Make this work with update, etc.
    # TODO: Make this work with named keys (rather than just auto ID).
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

    # TODO: Make this return value be a True/False (or something more useful).
    return self._rpc(dataset_id, 'commit', commit_request,
                     datastore_pb.CommitResponse)

  def delete_entity(self, dataset_id, key_pb):
    # TODO: Is this the right way to handle deleting
    #       (single and multiple as separate methods)?
    return self.delete_entities(dataset_id, [key_pb])

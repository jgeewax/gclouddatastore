import httplib2

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore import helpers
from gclouddatastore.dataset import Dataset


class Connection(object):
  """A connection to the Google Cloud Datastore via the Protobuf API.

  This class should understand only the basic types (and protobufs)
  in method arguments, however should be capable of returning advanced types.

  :type credentials: :class:`gclouddatastore.credentials.Credentials`
  :param credentials: The OAuth2 Credentials to use for this connection.
  """

  API_BASE_URL = 'https://www.googleapis.com'
  """The base of the API call URL."""

  API_VERSION = 'v1beta2'
  """The version of the API, used in building the API call's URL."""

  API_URL_TEMPLATE = ('{api_base}/datastore/{api_version}'
                      '/datasets/{dataset_id}/{method}')
  """A template used to craft the URL pointing toward a particular API call."""

  def __init__(self, credentials=None):
    self._credentials = credentials
    self._http = None

  @property
  def http(self):
    """A getter for the HTTP transport used in talking to the API.

    :rtype: :class:`httplib2.Http`
    :returns: A Http object used to transport data.
    """
    if not self._http:
      self._http = httplib2.Http()
      if self._credentials:
        self._http = self._credentials.authorize(self._http)
    return self._http

  def _request(self, dataset_id, method, data):
    """Make a request over the Http transport to the Cloud Datastore API.

    :type dataset_id: string
    :param dataset_id: The ID of the dataset of which to make the request.

    :type method: string
    :param method: The API call method name (ie, ``runQuery``, ``lookup``, etc)

    :type data: string
    :param data: The data to send with the API call.
                 Typically this is a serialized Protobuf string.

    :rtype: string
    :returns: The string response content from the API call.

    :raises: Exception if the response code is not 200 OK.
    """
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

    This method is used internally
    to come up with the URL
    to use when making RPCs
    to the Cloud Datastore API.

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
    """Factory method for Dataset objects.

    :param args: All args and kwargs will be passed along to the
                 :class:`gclouddatastore.dataset.Dataset` initializer.

    :rtype: :class:`gclouddatastore.dataset.Dataset`
    :returns: A dataset object that will use this connection as its transport.
    """
    kwargs['connection'] = self
    return Dataset(*args, **kwargs)

  def run_query(self, dataset_id, query_pb, namespace=None):
    """Run a query on the Cloud Datastore.

    Given a Query protobuf,
    sends a ``runQuery`` request to the Cloud Datastore API
    and returns a list of entity protobufs matching the query.

    You typically wouldn't use this method directly,
    in favor of the :func:`gclouddatastore.query.Query.fetch` method.

    Under the hood, the :class:`gclouddatastore.query.Query` class
    uses this method to fetch data:

    >>> import gclouddatastore
    >>> connection = gclouddatastore.get_connection(email, key_path)
    >>> dataset = connection.dataset('dataset-id')
    >>> query = dataset.query().kind('MyKind').filter('property =', 'value')

    Using the `fetch`` method...

    >>> query.fetch()
    [<list of Entity objects>]

    Under the hood this is doing...

    >>> connection.run_query('dataset-id', query.to_protobuf())
    [<list of Entity Protobufs>]

    :type dataset_id: string
    :param dataset_id: The ID of the dataset over which to run the query.

    :type query_pb: :class:`gclouddatastore.datastore_v1_pb2.Query`
    :param query_pb: The Protobuf representing the query to run.

    :type namespace: string
    :param namespace: The namespace over which to run the query.
    """
    request = datastore_pb.RunQueryRequest()

    if namespace:
      request.partition_id.namespace = namespace

    request.query.CopyFrom(query_pb)
    response = self._rpc(dataset_id, 'runQuery', request, datastore_pb.RunQueryResponse)
    return [e.entity for e in response.batch.entity_result]

  def lookup(self, dataset_id, key_pbs):
    """Lookup keys from a dataset in the Cloud Datastore.

    This method deals only with protobufs
    (:class:`gclouddatastore.datastore_v1_pb2.Key`
    and
    :class:`gclouddatastore.datastore_v1_pb2.Entity`)
    and is used under the hood for methods like
    :func:`gclouddatastore.dataset.Dataset.get_entity`:

    >>> import gclouddatastore
    >>> from gclouddatastore.key import Key
    >>> connection = gclouddatastore.get_connection(email, key_path)
    >>> dataset = connection.dataset('dataset-id')
    >>> key = Key(dataset=dataset).kind('MyKind').id(1234)

    Using the :class:`gclouddatastore.dataset.Dataset` helper:

    >>> dataset.get_entity(key)
    <Entity object>

    Using the ``connection`` class directly:

    >>> connection.lookup('dataset-id', key.to_protobuf())
    <Entity protobuf>

    :type dataset_id: string
    :param dataset_id: The dataset to look up the keys.

    :type key_pbs: list of :class:`gclouddatastore.datastore_v1_pb2.Key`
                   (or a single Key)
    :param key_pbs: The key (or keys) to retrieve from the datastore.

    :rtype: list of :class:`gclouddatastore.datastore_v1_pb2.Entity`
            (or a single Entity)
    :returns: The entities corresponding to the keys provided.
              If a single key was provided and no results matched,
              this will return None.
              If multiple keys were provided and no results matched,
              this will return an empty list.
    """
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
    """Delete keys from a dataset in the Cloud Datastore.

    This method deals only with
    :class:`gclouddatastore.datastore_v1_pb2.Key` protobufs
    and not with any of the other abstractions.
    For example, it's used under the hood in the
    :func:`gclouddatastore.entity.Entity.delete` method.

    :type dataset_id: string
    :param dataset_id: The dataset from which to delete the keys.

    :type key_pbs: list of :class:`gclouddatastore.datastore_v1_pb2.Key`
                   (or a single Key)
    :param key_pbs: The key (or keys) to delete from the datastore.
    """
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

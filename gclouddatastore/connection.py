import httplib2
import json

from gclouddatastore import datastore_v1_pb2 as datastore_pb
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

  def query(self, *args, **kwargs):
    query = Query(*args, **kwargs)
    query._connection = self
    return query

  def _run_query(self, query, namespace=None):
    request = datastore_pb.RunQueryRequest()

    if namespace:
      request.partition_id.namespace = namespace

    request.query.CopyFrom(query)

    payload = request.SerializeToString()
    headers = {
        'Content-Type': 'application/x-protobuf',
        'Content-Length': str(len(payload)),
        }
    headers, content = self.http.request(uri=self.api_url + 'runQuery',
        method='POST', headers=headers, body=payload)

    # TODO(jjg): Check if the response was valid or not.
    return datastore_pb.RunQueryResponse.FromString(content)

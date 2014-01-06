import copy
from itertools import izip

from gclouddatastore import datastore_v1_pb2 as datastore_pb


class Key(object):

  def __init__(self, dataset_id=None, namespace=None, path=None):
    self._dataset_id = dataset_id
    self._namespace = namespace
    self._path = path or [{'kind': ''}]

  def _clone(self):
    return copy.deepcopy(self)

  @classmethod
  def from_protobuf(cls, pb):
    key = cls(dataset_id=pb.partition_id.dataset_id)

    path = []
    for element in pb.path_element:
      element_dict = {'kind': element.kind}

      if element.HasField('id'):
        element_dict['id'] = element.id

      elif element.HasField('name'):
        element_dict['name'] = element.name

      path.append(element_dict)

    return cls(path=path, dataset_id=pb.partition_id.dataset_id)

  def to_protobuf(self):
    key = datastore_pb.Key()

    # Apparently 's~' is a prefix for High-Replication and is necessary here.
    dataset_id = self.dataset_id()
    if dataset_id:
      if not dataset_id.startswith('s~'):
        dataset_id = 's~' + self.dataset_id()

      key.partition_id.dataset_id = dataset_id

    if self._namespace:
      key.partition_id.namespace = self._namespace

    for item in self.path():
      element = key.path_element.add()
      if 'kind' in item:
        element.kind = item['kind']
      if 'id' in item:
        element.id = item['id']

    return key

  @classmethod
  def from_path(cls, *args, **kwargs):
    path = []
    items = iter(args)

    for kind, id_or_name in izip(items, items):
      entry = {'kind': kind}
      if isinstance(id_or_name, basestring):
        entry['name'] = id_or_name
      else:
        entry['id'] = id_or_name
      path.append(entry)

    kwargs['path'] = path
    return cls(**kwargs)

  def is_partial(self):
    return (self.id_or_name() is None)

  def dataset_id(self, dataset_id=None):
    if dataset_id:
      clone = self._clone()
      clone._dataset_id = dataset_id
      return clone
    else:
      return self._dataset_id

  def path(self, path=None):
    if path:
      clone = self._clone()
      clone._path = path
      return clone
    else:
      return self._path

  def kind(self, kind=None):
    if kind:
      clone = self._clone()
      clone._path[-1]['kind'] = kind
      return clone
    elif self.path():
      return self._path[-1]['kind']

  def id(self, id=None):
    if id:
      clone = self._clone()
      clone._path[-1]['id'] = id
      return clone
    elif self.path():
      return self._path[-1].get('id')

  def name(self, name=None):
    if name:
      clone = self._clone()
      clone._path[-1]['name'] = name
      return clone
    elif self.path():
      return self._path[-1].get('name')

  def id_or_name(self):
    return self.id() or self.name()

  def parent(self):
    raise NotImplementedError

  def __repr__(self):
    return '<Key%s>' % self.path()

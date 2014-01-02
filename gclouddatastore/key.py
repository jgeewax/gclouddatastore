from protobuf_to_dict import protobuf_to_dict


class Key(object):
  """The primary key for a datastore entity.

  A datastore GUID. A Key instance uniquely identifies an entity across all
  apps, and includes all information necessary to fetch the entity from the
  datastore.

  Key implements __hash__, and key instances are immutable, so Keys may be
  used in sets and as dictionary keys.
  """

  def __init__(self, dataset_id=None, namespace=None, path=None):
    self.dataset_id = dataset_id
    self.namespace = namespace
    self.path = path or []

  @classmethod
  def from_protobuf(cls, pb):
    key = cls(dataset_id=pb.partition_id.dataset_id)
    for element in pb.path_element:
      key.path.append({'kind': element.kind, 'id': element.id})
    return key

  @property
  def kind(self):
    if self.path:
      # Get the last item in the path's first element.
      return self.path[-1]['kind']

  @property
  def id_or_name(self):
    if self.path:
      return self.path[-1]['id']

  @property
  def parent(self):
    return None

  def __repr__(self):
    return '<{path}>'.format(path=self.path)

class Dataset(object):

  def __init__(self, id, connection=None):
    self._connection = connection
    self._id = id

  def connection(self):
    return self._connection

  def id(self):
    return self._id

  def query(self, *args, **kwargs):
    from gclouddatastore.query import Query
    kwargs['dataset'] = self
    return Query(*args, **kwargs)

  def entity(self, kind):
    from gclouddatastore.entity import Entity
    return Entity(dataset=self, kind=kind)

  def get_entity(self, key):
    """
    Retrieves an entity from the dataset, along with all of its attributes.

    :type key: :class:`gclouddatastore.key.Key`
    :param item_name: The name of the item to retrieve.

    :rtype: :class:`gclouddatastore.entity.Entity` or ``None``
    :return: The requested entity, or ``None`` if there was no match found.
    """
    return self.get_entities([key])

  def get_entities(self, keys):
    # This import is here to avoid circular references.
    from gclouddatastore.entity import Entity

    entity_pbs = self.connection().lookup(dataset_id=self.id(),
        key_pbs=[k.to_protobuf() for k in keys])

    entities = []
    for entity_pb in entity_pbs:
      entities.append(Entity.from_protobuf(entity_pb, dataset=self))
    return entities

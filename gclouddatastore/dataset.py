class Dataset(object):
  """A dataset in the Cloud Datastore.

  This class acts as an abstraction of a single dataset
  in the Cloud Datastore.

  A dataset is analogous to a database
  in relational database world,
  and corresponds to a single project
  using the Cloud Datastore.

  Typically, you would only have one of these per connection
  however it didn't seem right to collapse the functionality
  of a connection and a dataset together into a single class.

  Datasets (like :class:`gclouddatastore.query.Query`s)
  are immutable.
  That is, you cannot change the ID and connection
  references.
  If you need to modify the connection or ID,
  it's recommended to construct a new :class:`Dataset`.

  :type id: string
  :param id: The ID of the dataset (your project ID)

  :type connection: :class:`gclouddatastore.connection.Connection`
  :param connection: The connection to use for executing API calls.
  """

  def __init__(self, id, connection=None):
    self._connection = connection
    self._id = id

  def connection(self):
    """Get the current connection.

      >>> dataset = Dataset('dataset-id', connection=conn)
      >>> dataset.connection()
      <Connection object>

    :rtype: :class:`gclouddatastore.connection.Connection`
    :returns: Returns the current connection.
    """

    return self._connection

  def id(self):
    """Get the current dataset ID.

      >>> dataset = Dataset('dataset-id', connection=conn)
      >>> dataset.id()
      'dataset-id'

    :rtype: string
    :returns: The current dataset ID.
    """

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

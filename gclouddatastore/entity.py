from datetime import datetime

from gclouddatastore.key import Key


class Entity(dict):
  """
  Entities are mutable and act like a subclass of a dictionary.
  This means you could take an existing entity and change the key
  to duplicate the object.
  """

  def __init__(self, dataset=None, kind=None):
    if dataset and kind:
      self._key = Key(dataset=dataset).kind(kind)
    else:
      self._key = None

  def dataset(self):
    if self.key():
      return self.key().dataset()

  def key(self, key=None):
    if key:
      self._key = key
      return self
    else:
      return self._key

  def kind(self):
    if self.key():
      return self.key().kind()

  @classmethod
  def from_key(cls, key, load_properties=True):
    entity = cls().key(key)
    if load_properties:
      entity = entity.reload()
    return entity

  @classmethod
  def from_protobuf(cls, pb):
    # This is here to avoid circular imports.
    from gclouddatastore import helpers

    key = Key.from_protobuf(pb.key)
    entity = cls.from_key(key)

    for property_pb in pb.property:
      value = helpers.get_value_from_protobuf(property_pb)
      entity[property_pb.name] = value

    return entity

  def reload(self):
    """Reloads the contents of this entity from the datastore."""

    # Note that you must have a valid key, otherwise this makes no sense.
    entity = self.dataset().connection().get_entities(self.key().to_protobuf())

    # TODO(jjg): Raise an error if something dumb happens.
    if entity:
      self.update(entity)
    return self

  def save(self):
    key = self.dataset().connection().save_entity(
        dataset_id=self.dataset().id(), key_pb=self.key().to_protobuf(),
        properties=dict(self))
    self.key(Key.from_protobuf(key))
    return self

  def delete(self):
    response = self.dataset().connection().delete_entity(
        dataset_id=self.dataset().id(), key_pb=self.key().to_protobuf())

  def __repr__(self):
    # TODO: Make sure that this makes sense.
    # An entity should have a key all the time (even if it's partial).
    if self.key():
      return '<Entity%s %s>' % (self.key().path(), super(Entity, self).__repr__())
    else:
      return '<Entity %s>' % (super(Entity, self).__repr__())

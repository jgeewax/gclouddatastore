from datetime import datetime

from gclouddatastore import helpers
from gclouddatastore.key import Key


class Entity(dict):

  def __init__(self, key=None, connection=None):
    self._connection = connection
    self._key = key

  def key(self, key=None):
    if key:
      self._key = key
      return self
    else:
      return self._key

  @classmethod
  def from_protobuf(cls, pb):
    entity = cls(key=Key.from_protobuf(pb.key))

    for property_pb in pb.property:
      value = helpers.get_value_from_protobuf(property_pb)
      entity[property_pb.name] = value

    return entity

  def reload(self):
    """Reloads the contents of this entity from the datastore."""

    # Note that you must have a valid key, otherwise this makes no sense.
    entity = self._connection.get_entities(self.key())
    # TODO(jjg): Raise an error if something dumb happens.
    if entity:
      self.update(entity)
    return self

  def save(self):
    key = self._connection.save_entity(self)
    self.key(Key.from_protobuf(key))
    return self

  def delete(self):
    response = self._connection.delete_entities([self])

  def __repr__(self):
    # TODO: Make sure that this makes sense.
    # An entity should have a key all the time (even if it's partial).
    if self.key():
      return '<Entity%s %s>' % (self.key().path(), super(Entity, self).__repr__())
    else:
      return '<Entity %s>' % (super(Entity, self).__repr__())

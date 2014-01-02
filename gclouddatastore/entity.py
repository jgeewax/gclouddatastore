from datetime import datetime

from protobuf_to_dict import protobuf_to_dict
import pytz

from gclouddatastore.key import Key


class Entity(object):

  # TODO(jjg): Make this complete...
  VALUE_TYPES = ('boolean', 'double', 'integer', 'string')


  def __init__(self, key):
    self.key = key
    self.properties = {}

  @classmethod
  def from_protobuf(cls, pb):
    entity = cls(Key.from_protobuf(pb.key))

    for prop in pb.property:

      # datetime objects are handled differently, so try that first.
      if prop.value.HasField('timestamp_microseconds_value'):
        value = datetime.fromtimestamp(
            prop.value.timestamp_microseconds_value / 1e6)
        entity.properties[prop.name] = value.replace(tzinfo=pytz.utc)

      elif prop.value.HasField('key_value'):
        entity.properties[prop.name] = Key.from_protobuf(prop.value.key_value)

      else:
        # Try all the other types and see what we find.
        for value_type in cls.VALUE_TYPES:
          attr_name = value_type + '_value'
          if prop.value.HasField(attr_name):
            value = getattr(prop.value, attr_name)
            entity.properties[prop.name] = value
            break

    return entity

  def to_dict(self):
    return self.properties

  def __getattr__(self, name):
    if name in self.properties:
      return self.properties[name]

    raise AttributeError

  def __repr__(self):
    return '<%s, %s>' % (self.key.path, self.properties)

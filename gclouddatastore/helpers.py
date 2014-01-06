from datetime import datetime

import pytz

from gclouddatastore.key import Key


def get_protobuf_attribute_and_value(val):
  """Given a value, return the protobuf attribute name and proper value."""

  if isinstance(val, datetime):
    name, value = 'timestamp_microseconds', time.mktime(val.timetuple())
  elif isinstance(val, Key):
    name, value = 'key', val.to_protobuf()
  elif isinstance(val, bool):
    name, value = 'boolean', val
  elif isinstance(val, float):
    name, value = 'double', val
  elif isinstance(val, (int, long)):
    name, value = 'integer', val
  elif isinstance(val, basestring):
    name, value = 'string', val

  return name + '_value', value


def get_value_from_protobuf(pb):
  """Given a protobuf for a Property, get the value we care about."""

  if pb.value.HasField('timestamp_microseconds_value'):
    timestamp = pb.value.timestamp_microseconds_value / 1e6
    return datetime.fromtimestamp(timestamp).replace(tzinfo=pytz.utc)

  elif pb.value.HasField('key_value'):
    return Key.from_protobuf(pb.value.key_value)

  elif pb.value.HasField('boolean_value'):
    return pb.value.boolean_value

  elif pb.value.HasField('double_value'):
    return pb.value.double_value

  elif pb.value.HasField('integer_value'):
    return pb.value.integer_value

  elif pb.value.HasField('string_value'):
    return pb.value.string_value

  else:
    # TODO(jjg): Should we raise a ValueError here?
    return None

import copy

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore.entity import Entity


class Query(object):

  OPERATORS = {
      '<': datastore_pb.PropertyFilter.LESS_THAN,
      '<=': datastore_pb.PropertyFilter.LESS_THAN_OR_EQUAL,
      '>': datastore_pb.PropertyFilter.GREATER_THAN,
      '>=': datastore_pb.PropertyFilter.GREATER_THAN_OR_EQUAL,
      '=': datastore_pb.PropertyFilter.EQUAL,
      }

  def __init__(self, *kinds):
    self._connection = None
    self._query = datastore_pb.Query()
    self._namespace = None
    self.kind(*kinds)

  def _clone(self):
    # TODO(jjg): Double check that this makes sense...
    clone = copy.deepcopy(self)
    clone._connection = self._connection  # Shallow copy the connection.
    return clone

  def filter(self, expression, value):
    clone = self._clone()

    # Take an expression like 'property >=', and parse it into useful pieces.
    property_name, operator = None, None
    expression = expression.strip()

    for operator_string in self.OPERATORS:
      if expression.endswith(operator_string):
        operator = self.OPERATORS[operator_string]
        property_name = expression[0:-len(operator_string)].strip()

    if not operator or not property_name:
      raise ValueError('Invalid expression: "%s"' % expression)

    # Build a composite filter AND'd together.
    composite_filter = clone._query.filter.composite_filter
    composite_filter.operator = datastore_pb.CompositeFilter.AND

    # Add the specific filter
    property_filter = composite_filter.filter.add().property_filter
    property_filter.property.name = property_name
    property_filter.operator = operator

    # Set the value to filter on based on the type.
    # TODO(jjg): Handle Key's and datetime objects.
    # TODO(jjg): Factor this out somehow to use elsewhere.
    filter_value = property_filter.value
    if isinstance(value, bool):
      filter_value.boolean_value = value
    elif isinstance(value, basestring):
      filter_value.string_value = value
    elif isinstance(value, int):
      filter_value.integer_value = value
    elif isinstance(value, float):
      filter_value.double_value = value

    return clone

  def kind(self, *kinds):
    clone = self._clone()
    for kind in kinds:
      clone._query.kind.add().name = kind
    return clone

  def limit(self, limit):
    clone = self._clone()
    clone._query.limit = limit
    return clone

  def namespace(self, namespace):
    clone = self._clone()
    clone._namespace = namespace
    return clone

  def fetch(self, limit=None, connection=None):
    clone = self

    if limit:
      clone = self.limit(limit)

    connection = connection or clone._connection
    if not connection:
      raise ValueError

    response = connection._run_query(clone._query, namespace=clone._namespace)
    return [Entity.from_protobuf(e.entity) for e in response.batch.entity_result]

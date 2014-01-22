import copy

from gclouddatastore import datastore_v1_pb2 as datastore_pb
from gclouddatastore import helpers
from gclouddatastore.entity import Entity


# TODO: Figure out how to properly handle namespaces.

class Query(object):

  OPERATORS = {
      '<': datastore_pb.PropertyFilter.LESS_THAN,
      '<=': datastore_pb.PropertyFilter.LESS_THAN_OR_EQUAL,
      '>': datastore_pb.PropertyFilter.GREATER_THAN,
      '>=': datastore_pb.PropertyFilter.GREATER_THAN_OR_EQUAL,
      '=': datastore_pb.PropertyFilter.EQUAL,
      }

  def __init__(self, kinds=None, dataset=None):
    self._dataset = dataset
    self._pb = datastore_pb.Query()

    if kinds:
      self.kind(*kinds)

  def _clone(self):
    # TODO(jjg): Double check that this makes sense...
    clone = copy.deepcopy(self)
    clone._dataset = self._dataset  # Shallow copy the dataset.
    return clone

  def to_protobuf(self):
    return self._pb

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
    composite_filter = clone._pb.filter.composite_filter
    composite_filter.operator = datastore_pb.CompositeFilter.AND

    # Add the specific filter
    property_filter = composite_filter.filter.add().property_filter
    property_filter.property.name = property_name
    property_filter.operator = operator

    # Set the value to filter on based on the type.
    attr_name, pb_value = helpers.get_protobuf_attribute_and_value(value)
    setattr(property_filter.value, attr_name, pb_value)
    return clone

  def kind(self, *kinds):
    # TODO: Do we want this to be additive?
    #       If not, clear the _pb.kind attribute.
    if kinds:
      clone = self._clone()
      for kind in kinds:
        clone._pb.kind.add().name = kind
      return clone
    else:
      return self._pb.kind

  def limit(self, limit=None):
    if limit:
      clone = self._clone()
      clone._pb.limit = limit
      return clone
    else:
      return self._pb.limit

  def dataset(self, dataset=None):
    if dataset:
      clone = self._clone()
      clone._dataset = dataset
      return clone
    else:
      return self._dataset

  def fetch(self, limit=None):
    clone = self

    if limit:
      clone = self.limit(limit)

    entity_pbs = self.dataset().connection().run_query(
        query_pb=clone.to_protobuf(), dataset_id=self.dataset().id())

    return [Entity.from_protobuf(entity) for entity in entity_pbs]

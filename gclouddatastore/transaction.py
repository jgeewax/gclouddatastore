from gclouddatastore import datastore_v1_pb2 as datastore_pb


class Transaction(object):
  """An abstraction representing datastore Transactions.

  Transactions can be used
  to build up a bulk mutuation
  as well as provide isolation.

  For example,
  the following snippet of code
  will put the two ``save`` operations
  (either ``insert_auto_id`` or ``upsert``)
  into the same mutation, and execute those within a transaction::

    >>> import gclouddatastore
    >>> dataset = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> with dataset.transaction(bulk_mutation=True)  # The default.
    >>>   entity1.save()
    >>>   entity2.save()

  To rollback a transaction if there is an error::

    >>> import gclouddatastore
    >>> dataset = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> with dataset.transaction() as t:
    >>>   try:
    >>>     do_some_work()
    >>>     entity1.save()
    >>>   except:
    >>>     t.rollback()

  If the transaction isn't rolled back,
  it will commit by default.

  For now,
  this library will enforce a rule of
  one transaction per connection.
  That is,
  If you want to work with two transactions at the same time
  (for whatever reason),
  that must happen over two separate
  :class:`gclouddatastore.connection.Connection`s.

  For example, this is perfectly valid::

    >>> import gclouddatastore
    >>> dataset = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> with dataset.transaction():
    >>>   dataset.entity('Thing').save()

  However, this **wouldn't** be acceptable::

    >>> import gclouddatastore
    >>> dataset = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> with dataset.transaction():
    >>>   dataset.entity('Thing').save()
    >>>   with dataset.transaction():
    >>>     dataset.entity('Thing').save()

  Technically, it looks like the Protobuf API supports this type of pattern,
  however it makes the code particularly messy.
  If you really need to nest transactions, try::

    >>> import gclouddatastore
    >>> dataset1 = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> dataset2 = gclouddatastore.get_dataset('dataset-id', email, key_path)
    >>> with dataset1.transaction():
    >>>   dataset1.entity('Thing').save()
    >>>   with dataset2.transaction():
    >>>     dataset2.entity('Thing').save()
  """

  def __init__(self, dataset):
    self._dataset = dataset
    self._id = None
    self._mutation = datastore_pb.Mutation()

  def connection(self):
    return self.dataset().connection()

  def dataset(self):
    return self._dataset

  def id(self):
    return self._id

  def mutation(self):
    return self._mutation

  def rollback(self):
    self.connection().rollback_transaction(self.dataset().id(), self.id())
    self.connection().transaction(None)
    self._id = None

  def __enter__(self):
    self._id = self.connection().begin_transaction(self.dataset().id())
    self.connection().transaction(self)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    # It's possible that they called commit() already, in which case
    # we shouldn't do any committing of our own.
    if self.connection().transaction():
      self.connection().commit(self.dataset().id(), self.mutation())
      self.connection().transaction(None)

    self._id = None

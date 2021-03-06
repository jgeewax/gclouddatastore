Get started in 10 seconds
=========================

.. warning::
  This will use a *shared* dataset,
  which means any data you save
  will be available to anyone.

  If you want to create your own dataset,
  follow the
  (pretty simple)
  instructions in the
  :doc:`gettingstarted` guide.

Install the library
-------------------

The source code for the library
(and demo code)
lives on GitHub,
You can install the library quickly with ``pip``::

  $ pip install gclouddatastore

Run the example script included in the package::

  $ python -m gclouddatastore.demo.demo

If you're on Python 2.6::

  $ python -m gclouddatastore.demo.demo.__main__

(This file lives here:
https://github.com/jgeewax/gclouddatastore/blob/master/demo/demo.py)

Try it yourself
---------------

Crack open a Python interactive shell::

  $ python  # or ipython

And play with the demo dataset::

  >>> from gclouddatastore import demo
  >>> dataset = demo.get_dataset()

But once you have the dataset,
you can manipulate data in the datastore::

  >>> dataset.query('MyExampleKind').fetch()
  [<Entity{...}, ]
  >>> entity = dataset.entity('Person')
  >>> entity['name'] = 'Your name'
  >>> entity['age'] = 25
  >>> entity.save()
  >>> dataset.query('Person').fetch()
  [<Entity{...} {'name': 'Your name', 'age': 25}>]

The ``get_dataset`` method is just a shortcut for::

  >>> import gclouddatastore
  >>> from gclouddatastore import demo
  >>> dataset = gclouddatastore.get_dataset(
          demo.DATASET_ID, demo.CLIENT_EMAIL, demo.PRIVATE_KEY_PATH)

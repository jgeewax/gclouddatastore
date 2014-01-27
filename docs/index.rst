:tocdepth: 2

Google Cloud Datastore (Python API)
===================================

.. warning::
  This library is still under construction
  and is **not** the official Google Python API client library.
  See the `official documentation <https://developers.google.com/datastore/docs/apis/python/>`_.

What is it?
-----------

Google built this pretty neat data storage service
called Google Cloud Datastore.
This library makes it really really easy to interact
with the Cloud Datastore (save, query, etc)
in Python.

How can I kick the tires?
-------------------------

You can test things out
by following the :doc:`quickstart` guide,
which walks you through the basic features of the library
(and the service),
without requiring any real setup
(you don't even need a Google account).

How do I get it?
----------------

The ``gclouddatastore`` library is ``pip`` install-able::

  $ pip install gclouddatastore

If you have trouble installing
``pycrypto`` or ``pyopenssl``
(and you're on Ubuntu),
you can try install the precompiled packages::

  $ sudo apt-get install python-crypto python-openssl

If you want to install everything with ``pip``,
try installing the ``dev`` packages beforehand::

  $ sudo apt-get install python-dev libssl-dev

OK, I installed it. Now what?
-----------------------------

A good place to look is the guide: :doc:`gettingstarted`.

What about the full API docs?
-----------------------------

Check out the full :doc:`gclouddatastore`.

I found a bug!
--------------

Awesome!
The library is open source
and `lives on GitHub <https://github.com/jgeewax/gclouddatastore>`_.
Open an issue,
or fork the library and submit a pull request.

Indices and tables
------------------

.. toctree::
  :maxdepth: 1
  :hidden:

  index
  quickstart
  gettingstarted
  gclouddatastore

* :ref:`genindex`
* :ref:`modindex`

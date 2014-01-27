Google Cloud Datastore
======================

Incredibly quick demo
---------------------

Start by cloning the repository::

  $ git clone https://github.com/jgeewax/gclouddatastore.git
  $ cd gclouddatastore
  $ python setup.py develop

Then you should be all set to run the demo::

  $ python -m gclouddatastore.demo.demo

I'm getting weird errors... Can you help?
-----------------------------------------

Chances are you have some dependency problems,
if you're on Ubuntu,
try installing the pre-compiled packages::

  $ sudo apt-get install python-crypto python-openssl

or try installing the development packages
(that have the header files included)
and then ``pip install`` the dependencies again::

  $ sudo apt-get install python-dev libssl-dev

Where can I find more information?
----------------------------------

- http://gclouddatastore.readthedocs.org/en/latest/index.html
- http://gclouddatastore.readthedocs.org/en/latest/quickstart.html
- https://github.com/jgeewax/gclouddatastore/issues?state=open

How do I build the docs?
------------------------

  $ git clone ...
  $ cd gclouddatastore/docs
  $ make html

How do I run the tests?
-----------------------

  $ git clone ...
  $ nosetests

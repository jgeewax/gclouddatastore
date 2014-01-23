import sys

from gclouddatastore import __version__


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


if sys.version_info <= (2, 4):
  error = 'Requires Python Version 2.5 or above... exiting.'
  print >> sys.stderr, error
  sys.exit(1)


setup(name='gclouddatastore',
      version=__version__,
      description='API Client library for Google Cloud Datastore',
      author='JJ Geewax',
      author_email='jj@geewax.org',
      scripts=[],
      url='https://github.com/jgeewax/gclouddatastore',
      packages=['gclouddatastore'],
      package_data={},
      license='Apache 2.0',
      platforms='Posix; MacOS X; Windows',
      install_requires=['httplib2',
                        'oauth2client',
                        'pytz',
                        ],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Internet',
                   ]
      )

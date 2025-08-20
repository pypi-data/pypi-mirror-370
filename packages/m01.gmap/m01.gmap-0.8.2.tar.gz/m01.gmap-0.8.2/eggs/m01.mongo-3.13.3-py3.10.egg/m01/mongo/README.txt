======
README
======

IMPORTANT:
If you run the tests with the --all option a real mongodb stub server will
start at port 45017!

This package provides non persistent MongoDB object implementations. They can
simply get mixed with persistent.Persistent and contained.Contained if you like
to use them in a mixed MongoDB/ZODB application setup. We currently use this
framework as ORM (object relation mapper) where we map MongoDB objects
to python/zope schema based objects including validation etc.

In our last project, we started with a mixed ZODB/MongoDB application where we
mixed persistent.persistent into IMongoContainer objects. But later we where
so exited about the performance and stability that we removed the ZODB
persistence layer at all. Now we use a ZODB less setup in our application
where we start with a non persistent item as our application root. All required
tools where we use for such a ZODB less application setup are located in the
p01.publisher and p01.recipe.setup package.

NOTE: Some of this test use a fake mongodb located in m01/mongo/testing and some
other tests will use our mongdb stub from the m01.stub package. You can run
the tests with the --all option if you like to run the full tests which will
start and stop the mongodb stub server.

NOTE:
All mongo item interfaces will not provide ILocation or IContained but the
base mongo item implementations will implement Location which provides the
ILocation interface directly. This makes it simpler for permission
declaration in ZCML.


Setup
-----

from __future__ import absolute_import

  >>> from pprint import pprint
  >>> import pymongo
  >>> import zope.component
  >>> import m01.fake
  >>> from m01.mongo import interfaces


MongoClient
-----------

Setup a mongo client:

  >>> client = pymongo.MongoClient('localhost', 45017)
  >>> client
  MongoClient(host=['127.0.0.1:45017'])

As you can see the client is able to access the database:

  >>> db = client.m01MongoTesting
  >>> db
  Database(MongoClient(host=['127.0.0.1:45017']), u'm01MongoTesting')

A data base can retrun a collection:

  >>> collection = db['m01MongoTest']
  >>> collection
  Collection(Database(MongoClient(host=['127.0.0.1:45017']), u'm01MongoTesting'), u'm01MongoTest')

As you can see we can write to the collection:

  >>> result = collection.update_one({'_id': '123'}, {'$inc': {'counter': 1}},
  ...     upsert=True)
  >>> 'UpdateResult' in str(result)
  True

  >>> m01.fake.pprint(result.raw_result)
  {'n': 1, 'nModified': 0, 'ok': 1.0, 'updatedExisting': False, 'upserted': '123'}

And we can read from the collection:

  >>> collection.find_one({'_id': '123'})
  {u'_id': u'123', u'counter': 1}

Remove the result from our test collection:

  >>> result = collection.delete_one({'_id': '123'})
  >>> 'DeleteResult' in str(result)
  True

  >>> m01.fake.pprint(result.raw_result)
  {'n': 1, 'ok': 1.0}


tear down
---------

Now tear down our MongoDB database with our current MongoDB connection:

  >>> import time
  >>> time.sleep(1)
  >>> client.drop_database('m01MongoTesting')

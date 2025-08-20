Mapping source values
=====================

Sometimes a source provides the right choice of objects, but the actual values
we want to talk about are properties or computed views on those objects. The
`mapping proxy source` helps us to map a source to a different value space.

We start out with a source:

  >>> source = [1,2,3,4,5]

and we provide a method that maps the values of the original source to the
values we want to see (we map the numbers to the characters in the english
alphabet):

  >>> map = lambda x: chr(x+96)

Now we can create a mapped source:

  >>> from zc.sourcefactory.mapping import ValueMappingSource
  >>> mapped_source = ValueMappingSource(source, map)
  >>> list(mapped_source)
  ['a', 'b', 'c', 'd', 'e']
  >>> len(mapped_source)
  5
  >>> 'a' in mapped_source
  True
  >>> 1 in mapped_source
  False

You can also use context-dependent sources:

  >>> def bindSource(context):
  ...     return [1,2,3,4,5]
  >>> from zc.sourcefactory.mapping import ValueMappingSourceContextBinder
  >>> binder = ValueMappingSourceContextBinder(bindSource, map)
  >>> bound_source = binder(object())
  >>> list(bound_source)
  ['a', 'b', 'c', 'd', 'e']
  >>> len(bound_source)
  5
  >>> 'a' in bound_source
  True
  >>> 1 in bound_source
  False


Scaling
-------

Sometimes the number of items available through a source is very large.  So
large that you only want to access them if absolutely neccesary.  One such
occasion is with truth-testing a source.  By default Python will call
__nonzero__ to get the boolean value of an object, but if that isn't available
__len__ is called to see what it returns.  That might be very expensive, so we
want to make sure it isn't called.

  >>> class ExpensiveSource(object):
  ...     def __len__(self):
  ...         raise RuntimeError("oops, don't want to call __len__")
  ...
  ...     def __iter__(self):
  ...         return iter(range(999999))

  >>> expensive_source = ExpensiveSource()
  >>> mapped_source = ValueMappingSource(expensive_source, map)
  >>> bool(mapped_source)
  True

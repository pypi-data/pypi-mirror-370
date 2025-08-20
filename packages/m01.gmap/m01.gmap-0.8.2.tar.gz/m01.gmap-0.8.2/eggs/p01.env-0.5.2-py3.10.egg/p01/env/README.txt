======
README
======

getEnviron
----------

The method getEnviron allows to setup variables given from os.environ. This
can get used for setup a database connection uri or certificate path for a
more complex production server setup.

  >>> import os
  >>> import p01.env

See the buildout test setup located in buildout.cfg for a sample. Our test
setup provides the following variables:

  >>> print(p01.env.getEnviron('P01_ENV_TEST_UNICODE', required=True))
  42

  >>> print(p01.env.getEnviron('P01_ENV_TEST_STRING', required=True, rType=str))
  Hello World

  >>> p01.env.getEnviron('P01_ENV_TEST_BOOL', required=True, rType=bool)
  True

  >>> p01.env.getEnviron('P01_ENV_TEST_INT', required=True, rType=int)
  42


You can use your own converter:

  >>> def asTuple(v):
  ...     l = v.splitlines()
  ...     return tuple(l)


  >>> os.environ['P01_ENV_TEST_TUPLE'] = 'foo\nbar\nbaz'

  >>> p01.env.getEnviron('P01_ENV_TEST_TUPLE', rType=asTuple)
  ('foo', 'bar', 'baz')


Errors
------

The getEnviron tries to show usfull errors for missing or invalid values.

Missing value declared as required will end in ValueError:

  >>> p01.env.getEnviron('MISSING_OPTION', required=True)
  Traceback (most recent call last):
  ... 
  ValueError: p01.env requires "MISSING_OPTION" in your os.environ

A bad boolen will end as:

  >>> p01.env.getEnviron('P01_ENV_TEST_STRING', rType=bool)
  Traceback (most recent call last):
  ... 
  ValueError: p01.env requires "1, true, True, ok, yes, True" or "0, false, False, no, False" as "P01_ENV_TEST_STRING" boolean value and not: "Hello World"

A bad value will end as:

  >>> p01.env.getEnviron('P01_ENV_TEST_STRING', rType=int)
  Traceback (most recent call last):
  ... 
  ValueError: p01.env key "P01_ENV_TEST_STRING" convertion failed for value "Hello World" with error: "invalid literal for int() with base 10: 'Hello World'"


or a custom converter will show an error like:

  >>> def asFloat(v):
  ...     return float(v)

  >>> try:
  ...     p01.env.getEnviron('P01_ENV_TEST_STRING', rType=asFloat)
  ... except ValueError as ex:
  ...     print(ex)
  p01.env key "P01_ENV_TEST_STRING" convertion failed for value "Hello World" with error: "could not convert string to float: ...Hello World..."

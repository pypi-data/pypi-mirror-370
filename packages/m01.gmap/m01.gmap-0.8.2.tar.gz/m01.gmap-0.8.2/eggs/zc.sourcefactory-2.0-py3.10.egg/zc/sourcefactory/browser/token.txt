======
Tokens
======

Tokens are an identifying representation of an object, suitable for
transmission amongs URL-encoded data.

The sourcefactory package provides a few standard generators for tokens:

  >>> import zc.sourcefactory.browser.token

We have generators for strings:

  >>> zc.sourcefactory.browser.token.fromString('somestring')
  '1f129c42de5e4f043cbd88ff6360486f'

Unicode
=======

  Argh, I have to write the umlauts as unicode escapes otherwise
  distutils will have a encoding error in preparing upload to pypi:

  >>> zc.sourcefactory.browser.token.fromUnicode(
  ...     'somestring with umlauts \u00F6\u00E4\u00FC')
  '45dadc304e0d6ae7f4864368bad74951'

Integer
=======

  >>> zc.sourcefactory.browser.token.fromInteger(12)
  '12'

Persistent
==========

  >>> import persistent
  >>> class PersistentDummy(persistent.Persistent):
  ...     pass
  >>> p = PersistentDummy()
  >>> p._p_oid = 1234
  >>> zc.sourcefactory.browser.token.fromPersistent(p)
  '1234'

If an object is persistent but has not been added to a database yet, it will
be added to the database of it's __parent__:

  >>> root = rootFolder
  >>> p1 = PersistentDummy()
  >>> p1.__parent__ = root
  >>> zc.sourcefactory.browser.token.fromPersistent(p1)
  '0x01'

If an object has no parent, we fail:

  >>> p2 = PersistentDummy()
  >>> zc.sourcefactory.browser.token.fromPersistent(p2)
  Traceback (most recent call last):
  ...
  ValueError: Can not determine OID for <builtins.PersistentDummy object at 0x...>

Security proxied objects are unwrapped to get to their oid or connection
attribute:

  >>> from zope.security.proxy import ProxyFactory
  >>> p3 = PersistentDummy()
  >>> root['p3'] = p3
  >>> p3.__parent__ = root
  >>> p3p = ProxyFactory(p3)
  >>> p3p._p_jar
  Traceback (most recent call last):
    ...
  zope.security.interfaces.ForbiddenAttribute: ('_p_jar', <builtins.PersistentDummy object at 0x...>)

  >>> zc.sourcefactory.browser.token.fromPersistent(p3p)
  '0x02'


As a side-effect `p3` now has an _p_oid assigned.  When an object already has
an OID the connection is not queried, so a __parent__ would not be necessary:

  >>> del p3.__parent__
  >>> zc.sourcefactory.browser.token.fromPersistent(p3p)
  '0x02'


Interfaces
==========

  >>> from zope.interface import Interface
  >>> class I(Interface):
  ...     pass
  >>> zc.sourcefactory.browser.token.fromInterface(I)
  'builtins.I'

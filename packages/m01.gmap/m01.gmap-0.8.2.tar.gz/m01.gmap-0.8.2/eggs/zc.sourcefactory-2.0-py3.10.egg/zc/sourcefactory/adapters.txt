===========================
Common adapters for sources
===========================

To allow adapting factored sources specific to the factory, a couple of
standard interfaces that can be adapters are re-adapted as using a
multi-adapter for (FactoredSource, SourceFactory).

ISourceQueriables
=================

  >>> from zc.sourcefactory.basic import BasicSourceFactory
  >>> class Factory(BasicSourceFactory):
  ...     def getValues(self):
  ...         return [1,2,3]
  >>> source = Factory()

  >>> from zope.schema.interfaces import ISourceQueriables
  >>> import zope.interface
  >>> @zope.interface.implementer(ISourceQueriables)
  ... class SourceQueriables(object):
  ...     def __init__(self, source, factory):
  ...         self.source = source
  ...         self.factory = factory
  ...     def getQueriables(self):
  ...         return [('test', None)]

  >>> from zc.sourcefactory.source import FactoredSource
  >>> zope.component.provideAdapter(factory=SourceQueriables,
  ...                               provides=ISourceQueriables,
  ...                               adapts=(FactoredSource, Factory))

  >>> queriables = ISourceQueriables(source)
  >>> queriables.factory
  <Factory object at 0x...>
  >>> queriables.source
  <zc.sourcefactory.source.FactoredSource object at 0x...>
  >>> queriables.getQueriables()
  [('test', None)]

Cleanup
-------

  >>> zope.component.getSiteManager().unregisterAdapter(factory=SourceQueriables,
  ...     provided=ISourceQueriables, required=(FactoredSource, Factory))
  True

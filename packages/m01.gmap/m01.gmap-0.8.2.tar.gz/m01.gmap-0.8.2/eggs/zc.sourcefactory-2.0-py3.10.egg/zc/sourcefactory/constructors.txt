===================
Custom constructors
===================

Source factories are intended to behave as natural as possible. A side-effect
of using a custom factory method (__new__) on the base class is that
sub-classes may have a hard time if their constructor (__init__) has a
different signature.

zc.sourcefactory takes extra measures to allow using a custom constructor with
a different signature.

>>> import zc.sourcefactory.basic

>>> class Source(zc.sourcefactory.basic.BasicSourceFactory):
...
...     def __init__(self, values):
...         super(Source, self).__init__()
...         self.values = values
...
...     def getValues(self):
...         return self.values

>>> source = Source([1, 2, 3])
>>> list(source)
[1, 2, 3]

This is also true for contextual sources. The example is a bit silly
but it shows that it works in principal:

>>> import zc.sourcefactory.contextual
>>> default_values = (4, 5, 6)
>>> context_values = (6, 7, 8)
>>> class ContextualSource(
...     zc.sourcefactory.contextual.BasicContextualSourceFactory):
...
...     def __init__(self, defaults):
...         super(ContextualSource, self).__init__()
...         self.defaults = defaults
...
...     def getValues(self, context):
...         return self.defaults + context

>>> contextual_source = ContextualSource(default_values)(context_values)
>>> list(contextual_source)
[4, 5, 6, 6, 7, 8]

=====================================================
Browser views for sources created by source factories
=====================================================

Sources that were created using source factories already come with ready-made
terms and term objects.


Simple use
==========

Let's start with a simple source factory:

  >>> import zc.sourcefactory.basic
  >>> class DemoSource(zc.sourcefactory.basic.BasicSourceFactory):
  ...     def getValues(self):
  ...         return [b'a', b'b', b'c', b'd']
  >>> source = DemoSource()
  >>> list(source)
  [b'a', b'b', b'c', b'd']

We need a request first, then we can adapt the source to ITerms:

  >>> from zope.publisher.browser import TestRequest
  >>> import zope.browser.interfaces
  >>> import zope.component
  >>> request = TestRequest()
  >>> terms = zope.component.getMultiAdapter(
  ...     (source, request), zope.browser.interfaces.ITerms)
  >>> terms
  <zc.sourcefactory.browser.source.FactoredTerms object at 0x...>

For each value we get a factored term:

  >>> terms.getTerm(b'a')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>
  >>> terms.getTerm(b'b')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>
  >>> terms.getTerm(b'c')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>
  >>> terms.getTerm(b'd')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>

Unicode values are allowed as well:

  >>> terms.getTerm('\xd3')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>

Our terms are ITitledTokenizedTerm-compatible:

  >>> import zope.schema.interfaces
  >>> zope.schema.interfaces.ITitledTokenizedTerm.providedBy(
  ...     terms.getTerm('a'))
  True

In the most simple case, the title of a term is the string representation of
the object:

  >>> terms.getTerm('a').title
  'a'

If an adapter from the value to IDCDescriptiveProperties exists, the title
will be retrieved from this adapter:

  >>> import persistent
  >>> class MyObject(persistent.Persistent):
  ...    custom_title = 'My custom title'
  ...    _p_oid = 12
  >>> class DCDescriptivePropertiesAdapter(object):
  ...    def __init__(self, context):
  ...        self.title = context.custom_title
  ...        self.description = u""
  >>> from zope.component import provideAdapter
  >>> from zope.dublincore.interfaces import IDCDescriptiveProperties
  >>> provideAdapter(DCDescriptivePropertiesAdapter, [MyObject],
  ...     IDCDescriptiveProperties)
  >>> terms.getTerm(MyObject()).title
  'My custom title'

Extended use: provide your own titles
=====================================

Instead of relying on string representation or IDCDescriptiveProperties
adapters you can specify the `getTitle` method on the source factory to
determine the title for a value:

  >>> class DemoSourceWithTitles(DemoSource):
  ...     def getTitle(self, value):
  ...         return 'Custom title ' + value.custom_title
  >>> source2 = DemoSourceWithTitles()
  >>> terms2 = zope.component.getMultiAdapter(
  ...     (source2, request), zope.browser.interfaces.ITerms)
  >>> o1 = MyObject()
  >>> o1.custom_title = u"Object one"
  >>> o2 = MyObject()
  >>> o2.custom_title = u"Object two"
  >>> terms2.getTerm(o1).title
  'Custom title Object one'
  >>> terms2.getTerm(o2).title
  'Custom title Object two'


Extended use: provide your own tokens
=====================================

Instead of relying on default adapters to generate tokens for your values, you
can override the `getToken` method on the source factory to determine the
token for a value:

  >>> class DemoObjectWithToken(object):
  ...     token = None
  >>> o1 = DemoObjectWithToken()
  >>> o1.token = "one"
  >>> o2 = DemoObjectWithToken()
  >>> o2.token = "two"

  >>> class DemoSourceWithTokens(DemoSource):
  ...     values = [o1, o2]
  ...     def getValues(self):
  ...         return self.values
  ...     def getToken(self, value):
  ...         return value.token

  >>> source3 = DemoSourceWithTokens()
  >>> terms3 = zope.component.getMultiAdapter(
  ...     (source3, request), zope.browser.interfaces.ITerms)

  >>> terms3.getTerm(o1).token
  'one'
  >>> terms3.getTerm(o2).token
  'two'

Looking up by the custom tokens works as well:

  >>> terms3.getValue("one") is o1
  True
  >>> terms3.getValue("two") is o2
  True
  >>> terms3.getValue("three")
  Traceback (most recent call last):
  KeyError: "No value with token 'three'"


Value mapping sources
=====================

  XXX to come


Contextual sources
==================

Let's start with an object that we can use as the context:

  >>> zip_to_city = {'06112': 'Halle',
  ...                '06844': 'Dessa'}
  >>> import zc.sourcefactory.contextual
  >>> class DemoContextualSource(
  ...     zc.sourcefactory.contextual.BasicContextualSourceFactory):
  ...     def getValues(self, context):
  ...         return context.keys()
  ...     def getTitle(self, context, value):
  ...         return context[value]
  ...     def getToken(self, context, value):
  ...         return 'token-%s' % value
  >>> source = DemoContextualSource()(zip_to_city)
  >>> sorted(list(source))
  ['06112', '06844']

Let's look at the terms:

  >>> terms = zope.component.getMultiAdapter(
  ...     (source, request), zope.browser.interfaces.ITerms)
  >>> terms
  <zc.sourcefactory.browser.source.FactoredContextualTerms object at 0x...>

For each value we get a factored term with the right title from the context:

  >>> terms.getTerm('06112')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>
  >>> terms.getTerm('06112').title
  'Halle'
  >>> terms.getTerm('06844')
  <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>
  >>> terms.getTerm('06844').title
  'Dessa'
  >>> terms.getTerm('06844').token
  'token-06844'

And in reverse we can get the value for a given token as well:

  >>> terms.getValue('token-06844')
  '06844'

Interfaces
==========

Both the FactoredSource and FactoredContextualSource have associated
interfaces.

  >>> from zc.sourcefactory import interfaces
  >>> from zc.sourcefactory import source
  >>> from zope import interface
  >>> interface.classImplements(
  ...     source.FactoredSource, interfaces.IFactoredSource)
  >>> interface.classImplements(
  ...     source.FactoredContextualSource, interfaces.IContextualSource)

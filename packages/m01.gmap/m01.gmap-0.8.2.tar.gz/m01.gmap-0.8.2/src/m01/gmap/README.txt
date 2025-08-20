======
README
======

This package provides a z3c.form widget concept for google maps. For more info
about google maps see: http://code.google.com/apis/maps/.

  >>> import os
  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget
  >>> from z3c.form.interfaces import INPUT_MODE
  >>> from z3c.form.testing import TestRequest
  >>> from z3c.form.widget import WidgetTemplateFactory
  >>> import m01.gmap
  >>> import m01.gmap.util
  >>> import m01.gmap.browser
  >>> from m01.gmap import interfaces
  >>> from m01.gmap.widget import GMapWidget
  >>> from m01.gmap.widget import GeoPointGMapWidget


GMapWidget
----------

The google map (GMapWidget) widget allows you to show a map for select latitude
and longitude for a geo location in input mode. In display mode it offers a
GMap which shows the given location.

As for all widgets, the GMap widget must provide the ``IWidget``
interface:

  >>> verifyClass(IWidget, GMapWidget)
  True

The widget can be instantiated only using the request:

  >>> request = TestRequest()
  >>> widget = GMapWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

We also need to register the template for the widget:

  >>> def getPath(filename):
  ...     return os.path.join(os.path.dirname(m01.gmap.__file__),
  ...     filename)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('widget_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IGMapWidget),
  ...     IPageTemplate, name=INPUT_MODE)

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="hidden" id="widget.id-latitude" name="widget.name-latitude" class="hidden-widget" value="" />
  <input type="hidden" id="widget.id-longitude" name="widget.name-longitude" class="hidden-widget" value="" />
  <div id="widget.id" style="width: 400px; height: 300px"></div>
  <script type="text/javascript">
    $("#widget\\.id").m01GMapWidget({
      mode: "input",
      infoWindowContent: "Drag and drop the marker and save the form. <br />Double click the marker for remove them.",
      latitude: null,
      longitude: null,
      latitudeFallback: 10,
      longitudeFallback: 10,
      latitudeExpression: "#widget\\.id-latitude",
      longitudeExpression: "#widget\\.id-longitude",
      address: "",
      zoom: 11,
      zoomFallback: 4,
      iconURL: "http://127.0.0.1/@@/m01GMapWidgetIcon.png",
      iconWidth: 19,
      iconHeight: 32,
      iconAnchorXOffset: 9,
      iconAnchorYOffset: 30,
      infoWindowAnchorXOffset: 10,
      infoWindowAnchorYOffset: 0,
      responsive: true,
      iconShadowURL: "http://127.0.0.1/@@/m01GMapWidgetIconShadow.png"
    });
  </script>
  <BLANKLINE>

We also need to include the IGMapAPIProvider which knows how to generate the
gamp api javascipt. The APi key it'self can get defined with a product config
or with a envirnoment setup. See buildout.cfg and util.py for more info:

  >>> print(m01.gmap.util.GMAP_API_KEY)
  ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw

We offer http or https javascript links:

  >>> print(m01.gmap.util.GMAP_JAVASCRIPT)
  <script type="text/javascript" src="//maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

  >>> print(m01.gmap.util.GMAP_HTTPS_JAVASCRIPT)
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

And you content provider can get used for render the full javascript:

  >>> provider = m01.gmap.browser.GMapAPIProvider(None, None, None)
  >>> print(provider.render())
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>



GeoPointGMapWidget
------------------

The GeoPointGMapWidget widget provides the same as the GMapWidget but uses
another converter and support the m01.mongo GeoPoint implementation.

As for all widgets, the GMap widget must provide the ``IWidget``
interface:

  >>> verifyClass(IWidget, GeoPointGMapWidget)
  True

The widget can be instantiated only using the request:

  >>> request = TestRequest()
  >>> widget = GeoPointGMapWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

We also need to register the template for the widget:

  >>> def getPath(filename):
  ...     return os.path.join(os.path.dirname(m01.gmap.__file__),
  ...     filename)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('widget_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IGeoPointGMapWidget),
  ...     IPageTemplate, name=INPUT_MODE)

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="hidden" id="widget.id-latitude" name="widget.name-latitude" class="hidden-widget" value="" />
  <input type="hidden" id="widget.id-longitude" name="widget.name-longitude" class="hidden-widget" value="" />
  <div id="widget.id" style="width: 400px; height: 300px"></div>
  <script type="text/javascript">
    $("#widget\\.id").m01GMapWidget({
      mode: "input",
      infoWindowContent: "Drag and drop the marker and save the form. <br />Double click the marker for remove them.",
      latitude: null,
      longitude: null,
      latitudeFallback: 10,
      longitudeFallback: 10,
      latitudeExpression: "#widget\\.id-latitude",
      longitudeExpression: "#widget\\.id-longitude",
      address: "",
      zoom: 11,
      zoomFallback: 4,
      iconURL: "http://127.0.0.1/@@/m01GMapWidgetIcon.png",
      iconWidth: 19,
      iconHeight: 32,
      iconAnchorXOffset: 9,
      iconAnchorYOffset: 30,
      infoWindowAnchorXOffset: 10,
      infoWindowAnchorYOffset: 0,
      responsive: true,
      iconShadowURL: "http://127.0.0.1/@@/m01GMapWidgetIconShadow.png"
    });
  </script>
  <BLANKLINE>

We also need to include the IGMapAPIProvider which knows how to generate the
gamp api javascipt. The APi key it'self can get defined with a product config
or with a envirnoment setup. See buildout.cfg and util.py for more info:

  >>> print(m01.gmap.util.GMAP_API_KEY)
  ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw

We offer http or https javascript links:

  >>> print(m01.gmap.util.GMAP_JAVASCRIPT)
  <script type="text/javascript" src="//maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

  >>> print(m01.gmap.util.GMAP_HTTPS_JAVASCRIPT)
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

And you content provider can get used for render the full javascript:

  >>> provider = m01.gmap.browser.GMapAPIProvider(None, None, None)
  >>> print(provider.render())
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

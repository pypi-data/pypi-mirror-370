###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.i18n
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.component import hooks

from z3c.form import widget

from z3c.form.interfaces import NOVALUE
from z3c.form import widget
from z3c.form import validator
from z3c.form import converter
from z3c.form.browser import text

from m01.gmap import interfaces
from m01.gmap import schema

try:
    unicode
except Exception as e:
    unicode = str

_ = zope.i18nmessageid.MessageFactory('p01')


m01_gmap_template = """<script type="text/javascript">
  $("#%s").m01GMapWidget({%s
  });
</script>
"""

def m01GMapWidgetJavaScript(m01GMapExpression, data):
    """GMap JavaScript generator.

    Knows how to generate customization for m01GMap JS.
    This is usefull for generate custom image path.

    The data argument allows you to set key, value pairs for customized data.
    """

    lines = []
    append = lines.append
    for key, value in data.items():
        if key == 'mapType':
            if value is None:
                # skip empty mapType, use script defaults
                continue
            append('\n    mapType: %s' % value)
        elif value is True:
            append('\n    %s: true' % key)
        elif value is False:
            append('\n    %s: false' % key)
        elif value is None:
            append('\n    %s: null' % key)
        elif isinstance(value, int):
            append('\n    %s: %s' % (key, value))
        elif isinstance(value, (str, unicode)):
            if value.startswith('$'):
                append('\n    %s: %s' % (key, value))
            else:
                append('\n    %s: "%s"' % (key, value))
        else:
            append('\n    %s: %s' % (key, value))
    options = ','.join(lines)

    return m01_gmap_template % (m01GMapExpression, options)


class GMapWidgetBase(text.TextWidget):
    """Generic google map widget"""

    _siteURL = None

    # widget options
    css = u'm01-gmap'

    # map config
    mapType = None
    width = 400
    height = 300
    responsive = True
    zoom = 11

    # info window content for display widget mode
    infoWindowMessageDisplayMode = u''

    # info window content for input widget mode
    infoWindowMessageInputMode = _(
        u'Drag and drop the marker and save the form. <br />'
        u'Double click the marker for remove them.')

    # marker icon config
    iconName = 'm01GMapWidgetIcon.png'
    iconShadowName = 'm01GMapWidgetIconShadow.png'
    iconWidth = 19
    iconHeight = 32
    iconAnchorXOffset = 9
    iconAnchorYOffset = 30

    # info window config
    infoWindowAnchorXOffset = 10
    infoWindowAnchorYOffset = 0

    latitudeFallback = 10
    longitudeFallback = 10
    zoomFallback = 4

    # enable remove geo location
    removeMarkerOnDBClick = True

    # widget update will override this value
    value = {'lat': u'', 'lon': u''}

    @property
    def style(self):
        return 'width: %spx; height: %spx' % (self.width, self.height)

    @property
    def siteURL(self):
        if self._siteURL is None:
            site = hooks.getSite()
            self._siteURL = absoluteURL(site, self.request)
        return self._siteURL

    @property
    def iconURL(self):
        return '%s/@@/%s' % (self.siteURL, self.iconName)

    @property
    def iconShadowURL(self):
        if self.iconShadowName is not None:
            return '%s/@@/%s' % (self.siteURL, self.iconShadowName)

    @property
    def infoWindowContent(self):
        if self.mode == 'display':
            msg = self.infoWindowMessageDisplayMode
            return zope.i18n.translate(msg, context=self.request)
        if self.mode == 'input':
            msg = self.infoWindowMessageInputMode
            return zope.i18n.translate(msg, context=self.request)
        return u''

    @property
    def address(self):
        """Simple address lookup.

        Note that this implementation requires the following attributes given
        from the context:

        street, city, state, zip, country

        The result will be in the US format which fits for other countries too
        even if the format is not 100% correct. The generated address looks
        like:

        street, city, state zip, country

        Note, the state and zip do not contain a comma. Also note that the
        country must be a real country name and not a iso country code.

        If this doesn't fit, feel free to implement your own configuration
        and register them as IGMapWidgetConfiguration adapter with
        (context, request, gmap or None, view, field, widget) as discriminators.
        """
        args = []
        append = args.append
        if self.context is not None:
            # plain widget setup doesn't provide a context
            if self.context.street:
                append(self.context.street)
            if self.context.city:
                append(self.context.city)
            if self.context.state and self.context.zip:
                append('%s %s' % (self.context.state, self.context.zip))
            elif self.context.state and not self.context.zip:
                append(self.context.state)
            elif not self.context.state and self.context.zip:
                append(self.context.zip)
            if self.context.country:
                append(self.context.country)
        return ', '.join(args)

    @property
    def names(self):
        return {'lat': '%s-latitude' % self.name,
                'lon': '%s-longitude' % self.name}

    @property
    def ids(self):
        return {'lat': '%s-latitude' % self.id,
                'lon': '%s-longitude' % self.id}

    def extract(self, default=NOVALUE, setErrors=True):
        """See z3c.form.interfaces.IWidget."""
        value = {}
        for key, name in self.names.items():
            val = self.request.get(name, None)
            if val is not None:
                value[key] = val
        return value or NOVALUE

    @property
    def gMapJavaScript(self):
        latId = self.ids['lat']
        lngId = self.ids['lon']
        latitudeExpression = '#%s' % latId.replace('.', '\\\.')
        longitudeExpression = '#%s' % lngId.replace('.', '\\\.')
        data = {
            # internal generated widget values
            'mode': self.mode,
            'infoWindowContent': self.infoWindowContent,
            'latitude': self.value.get('lat') or None,
            'longitude': self.value.get('lon') or None,
            'latitudeFallback': self.latitudeFallback,
            'longitudeFallback': self.longitudeFallback,
            'latitudeExpression': latitudeExpression,
            'longitudeExpression': longitudeExpression,
            'address': self.address,
            'zoom': self.zoom,
            'zoomFallback': self.zoomFallback,
            'iconURL': self.iconURL,
            'iconWidth': self.iconWidth,
            'iconHeight': self.iconHeight,
            'iconAnchorXOffset': self.iconAnchorXOffset,
            'iconAnchorYOffset': self.iconAnchorYOffset,
            'infoWindowAnchorXOffset': self.infoWindowAnchorXOffset,
            'infoWindowAnchorYOffset': self.infoWindowAnchorYOffset,
            'responsive': self.responsive,
           }
        if self.mapType is not None:
            data['mapType'] = self.mapType
        if self.iconShadowName is not None:
            data['iconShadowURL'] = self.iconShadowURL
        m01GMapWidgetExpression = self.id.replace('.', '\\\.')
        return m01GMapWidgetJavaScript(m01GMapWidgetExpression, data)


@zope.interface.implementer_only(interfaces.IGMapWidget)
class GMapWidget(GMapWidgetBase):
    """Generic google map widget"""


def getGMapWidget(field, request):
    """IFieldWidget factory for GMapWidget."""
    # add gmap widget marker to annotations
    request.annotations['m01.gmap.widget.GMapWidget'] = True
    return widget.FieldWidget(field, GMapWidget(request))


@zope.interface.implementer_only(interfaces.IGeoPointGMapWidget)
class GeoPointGMapWidget(GMapWidgetBase):
    """GeoPoint google map widget"""


def getGeoPointGMapWidget(field, request):
    """IFieldWidget factory for GeoPointGMapWidget."""
    # add gmap widget marker to annotations
    request.annotations['m01.gmap.widget.GMapWidget'] = True
    return widget.FieldWidget(field, GeoPointGMapWidget(request))

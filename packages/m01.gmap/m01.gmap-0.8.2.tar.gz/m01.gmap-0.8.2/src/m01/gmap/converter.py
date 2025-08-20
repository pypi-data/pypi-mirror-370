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

import zope.schema
import zope.component

from z3c.form import converter

import  m01.mongo.geo

from m01.gmap import interfaces


class GMapWidgetDataConverterBase(converter.BaseDataConverter):
    """GMapWidget data converter base class."""

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is None:
            lon = ''
            lat = ''
        elif isinstance(value, dict):
            if value.get('coordinates'):
                # GeoPoint
                coordinates = value.get('coordinates')
                if coordinates and len(coordinates) == 2:
                    # set lon, lat
                    lon = coordinates[0]
                    lat = coordinates[1]
            else:
                # GeoLocation
                lon = value.get('lon')
                lat = value.get('lat')
        elif isinstance(value, (list, tuple)):
            lon = value[0]
            lat = value[1]
        else:
            lon = value.lon
            lat = value.lat
        return {'lon' : lon, 'lat': lat}

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        lon = value.get('lon')
        lat = value.get('lat')
        if lon and lat:
            geoLocation = self.field.get(self.widget.context)
            if geoLocation is None:
                geoLocation = self.geoObjectFactory({'lon':lon, 'lat': lat})
                geoLocation.__parent__ = self.widget.context
                geoLocation.__name__ = unicode(self.field.__name__)
            else:
                # just set the values, we will prevent write access in the
                # GeoLocation implementation itself if the value is the same
                geoLocation.lon = float(lon)
                geoLocation.lat = float(lat)
            return geoLocation
        else:
            return None


class GMapWidgetDataConverter(GMapWidgetDataConverterBase):
    """GMapWidget data converter for IGeoLocation objects."""

    zope.component.adapts(zope.schema.Object,
        interfaces.IGMapWidget)

    geoObjectFactory = m01.mongo.geo.GeoLocation


class GeoPointGMapWidgetDataConverter(GMapWidgetDataConverterBase):
    """GeoPointGMapWidget data converter for IGeoPoint objects."""

    zope.component.adapts(zope.schema.Object,
        interfaces.IGeoPointGMapWidget)

    geoObjectFactory = m01.mongo.geo.GeoPoint

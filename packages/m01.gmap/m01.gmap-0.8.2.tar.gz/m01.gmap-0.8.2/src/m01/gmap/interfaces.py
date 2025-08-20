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
import zope.contentprovider.interfaces

from z3c.form.interfaces import IWidget


class IGMapAPIProvider(zope.contentprovider.interfaces.IContentProvider):
    """Gmap api javascript provider interface"""


class IHTTPSGMapAPIProvider(IGMapAPIProvider):
    """Gmap api javascript provider interface supporting https"""


class IGMapWidgetSchema(IWidget):
    """Google map widget schema."""

    # implement your own address lookup if the default street, city etc.
    # doesn't fit
    address = zope.schema.TextLine(
        title=u'Google Map address',
        description=u'The google map geo location address string.',
        default=None,
        missing_value=u'',
        required=True)

    mapType = zope.schema.Choice(
        title=u'Google map type',
        description=u'The google map type',
        values=[u'G_NORMAL_MAP', u'G_SATELLITE_MAP', u'G_HYBRID_MAP'],
        default=u'G_NORMAL_MAP',
        required=True)

    width = zope.schema.Int(
        title=u'Map width',
        description=u'The map width in pixle',
        default=500,
        required=True)

    height = zope.schema.Int(
        title=u'Map height in pixle',
        description=u'The map height in pixle',
        default=400,
        required=True)

    iconName = zope.schema.TextLine(
        title=u'Map marker icon name',
        description=u'The map marker icon name',
        required=True)

    iconShadowName = zope.schema.TextLine(
        title=u'Map marker icon shadow name',
        description=u'The map marker icon shadow name',
        required=True)

    iconURL = zope.schema.URI(
        title=u'Map marker icon url',
        description=u'The map marker icon url',
        required=True)

    iconShadowURL = zope.schema.URI(
        title=u'Map marker icon shadow url',
        description=u'The map marker icon url',
        required=True)

    iconWidth = zope.schema.Int(
        title=u'Map marker icon width in pixle',
        description=u'The map marker icon width in pixle',
        default=19,
        required=True)

    iconHeight = zope.schema.Int(
        title=u'Map marker icon height',
        description=u'The map marker icon height',
        default=32,
        required=True)

    iconAnchorXOffset = zope.schema.Int(
        title=u'Icon anchor offset x',
        description=u'The icon anchor offset x',
        default=9,
        required=True)

    iconAnchorYOffset = zope.schema.Int(
        title=u'Icon anchor offset y',
        description=u'The icon anchor offset y',
        default=30,
        required=True)

    infoWindowAnchorXOffset = zope.schema.Int(
        title=u'Icon window anchor offset x',
        description=u'The icon window anchor offset x',
        default=10,
        required=True)

    infoWindowAnchorYOffset = zope.schema.Int(
        title=u'Icon window anchor offset y',
        description=u'The icon window anchor offset y',
        default=0,
        required=True)

    zoom = zope.schema.Int(
        title=u'Zoom factor',
        description=u'The map zoom factor',
        default=10,
        required=True)

    infoWindowContent = zope.schema.TextLine(
        title=u'Message used for info window',
        description=u'The message used for info window',
        default=u'',
        required=True)

    infoWindowMessageDisplayMode = zope.schema.TextLine(
        title=u'Content shown in google map info window for display mode',
        description=u'The info window content for display widget mode. If an '
                      'empty string is used no info window is shown',
        default=u'',
        required=True)

    infoWindowMessageInputMode = zope.schema.TextLine(
        title=u'Content shown in google map info window for input mode',
        description=u'The content get used in the google map info window popup.',
        default=u'',
        required=True)


class IGMapWidget(IGMapWidgetSchema):
    """GeoLocation GMapWidget schema"""


class IGeoPointGMapWidget(IGMapWidgetSchema):
    """GeoPoint GMapWidget schema"""

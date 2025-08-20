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
import zope.publisher.interfaces.http

import m01.gmap.util

from m01.gmap import interfaces


class GMapAPIProviderBase(object):
    """Gmap api provider base class"""

    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.http.IHTTPRequest,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass


@zope.interface.implementer(interfaces.IGMapAPIProvider)
class GMapAPIProvider(GMapAPIProviderBase):
    """Gmap api provider.

    Use this GMap api key provider in your pagetemplate like:
    
    <tal:block replace="structure provider:IGMapAPIProvider"> </tal:block>
    
    """

    def render(self):
        return m01.gmap.util.GMAP_HTTPS_JAVASCRIPT


@zope.interface.implementer(interfaces.IHTTPSGMapAPIProvider)
class HTTPSGMapAPIProvider(GMapAPIProviderBase):
    """Gmap api provider supporting https API call.

    Use this GMap api key provider in your pagetemplate like:
    
    <tal:block replace="structure provider:IHTTPSGMapAPIProvider"> </tal:block>
    
    """

    def render(self):
        return m01.gmap.util.GMAP_HTTPS_JAVASCRIPT

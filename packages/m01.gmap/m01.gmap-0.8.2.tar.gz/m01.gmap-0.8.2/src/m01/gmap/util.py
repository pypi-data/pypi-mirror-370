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

import os

from zope.app.appsetup.product import getProductConfiguration

try:
    unicode
except Exception as e:
    unicode = str


JAVASCRIPT_TEMPLATE = """<script type="text/javascript" src="%s"> </script>"""


def getConfig(product, confKey, envKey, required=True):
    """Get product configuration based on zope.app.appsetup or env variable."""
    value = None
    config = getProductConfiguration(product)
    if config is not None:
        value = config.get(confKey)
    else:
        value = os.environ.get(envKey)
    if value is None and required:
        raise ValueError(
            "You must define '%s' product config '%s' in buildout.cfg" % (
                confKey, product))
    if value:
        return unicode(value)


# Google Map API key loaded from m01.gmap product config or env variable
GMAP_API_KEY = getConfig('m01.gmap', 'key', 'M01_GMAP_API_KEY', required=False)


def getGMapJavaScript(apiKey, protocol='http'):
    """Google Map API key based on M01_GMAP_API_KEY value"""
    if protocol:
        protocol += ':'
        protocol = protocol.replace('::', ':')
    if apiKey is None:
        return ''
    srcURL = '%s//maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % (protocol,
        apiKey)
    return JAVASCRIPT_TEMPLATE % srcURL

# GMAP JavaScript
GMAP_JAVASCRIPT = getGMapJavaScript(GMAP_API_KEY, '')
GMAP_HTTP_JAVASCRIPT = getGMapJavaScript(GMAP_API_KEY, 'http')
GMAP_HTTPS_JAVASCRIPT = getGMapJavaScript(GMAP_API_KEY, 'https')

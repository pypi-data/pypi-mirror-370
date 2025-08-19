# Copyright (c) 2013 Steve Canny, https://github.com/scanny
#
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# See LICENSE in the project root for full license information.



# encoding: utf-8

"""
Provides StylesPart and related objects
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from ..opc.constants import CONTENT_TYPE as CT
from ..opc.packuri import PackURI
from ..opc.part import XmlPart
from ..oxml import parse_xml
from ..styles.styles import Styles


class StylesPart(XmlPart):
    """
    Proxy for the styles.xml part containing style definitions for a document
    or glossary.
    """
    @classmethod
    def default(cls, package):
        """
        Return a newly created styles part, containing a default set of
        elements.
        """
        partname = PackURI('/word/styles.xml')
        content_type = CT.WML_STYLES
        element = parse_xml(cls._default_styles_xml())
        return cls(partname, content_type, element, package)

    @property
    def styles(self):
        """
        The |_Styles| instance containing the styles (<w:style> element
        proxies) for this styles part.
        """
        return Styles(self.element)

    @classmethod
    def _default_styles_xml(cls):
        """
        Return a bytestream containing XML for a default styles part.
        """
        path = os.path.join(
            os.path.split(__file__)[0], '..', 'templates',
            'default-styles.xml'
        )
        with open(path, 'rb') as f:
            xml_bytes = f.read()
        return xml_bytes

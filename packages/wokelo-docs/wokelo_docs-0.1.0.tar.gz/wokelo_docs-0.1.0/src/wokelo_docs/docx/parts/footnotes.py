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



from __future__ import absolute_import, division, print_function, unicode_literals

from ..opc.constants import CONTENT_TYPE as CT
from ..opc.packuri import PackURI
from ..opc.part import XmlPart
from ..oxml import parse_xml

import os

class FootnotesPart(XmlPart):
    """
    Definition of Footnotes Part
    """
    @classmethod
    def default(cls, package):
        partname = PackURI("/word/footnotes.xml")
        content_type = CT.WML_FOOTNOTES
        element = parse_xml(cls._default_footnotes_xml())
        return cls(partname, content_type, element, package)

    @classmethod
    def _default_footnotes_xml(cls):
        path = os.path.join(os.path.split(__file__)[0], '..', 'templates', 'default-footnotes.xml')
        with open(path, 'rb') as f:
           xml_bytes = f.read()
        return xml_bytes 
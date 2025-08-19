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

"""Header and footer part objects"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from wokelo_docs.docx.opc.constants import CONTENT_TYPE as CT
from wokelo_docs.docx.oxml import parse_xml
from wokelo_docs.docx.parts.story import BaseStoryPart


class FooterPart(BaseStoryPart):
    """Definition of a section footer."""

    @classmethod
    def new(cls, package):
        """Return newly created footer part."""
        partname = package.next_partname("/word/footer%d.xml")
        content_type = CT.WML_FOOTER
        element = parse_xml(cls._default_footer_xml())
        return cls(partname, content_type, element, package)

    @classmethod
    def _default_footer_xml(cls):
        """Return bytes containing XML for a default footer part."""
        path = os.path.join(
            os.path.split(__file__)[0], '..', 'templates', 'default-footer.xml'
        )
        with open(path, 'rb') as f:
            xml_bytes = f.read()
        return xml_bytes


class HeaderPart(BaseStoryPart):
    """Definition of a section header."""

    @classmethod
    def new(cls, package):
        """Return newly created header part."""
        partname = package.next_partname("/word/header%d.xml")
        content_type = CT.WML_HEADER
        element = parse_xml(cls._default_header_xml())
        return cls(partname, content_type, element, package)

    @classmethod
    def _default_header_xml(cls):
        """Return bytes containing XML for a default header part."""
        path = os.path.join(
            os.path.split(__file__)[0], '..', 'templates', 'default-header.xml'
        )
        with open(path, 'rb') as f:
            xml_bytes = f.read()
        return xml_bytes

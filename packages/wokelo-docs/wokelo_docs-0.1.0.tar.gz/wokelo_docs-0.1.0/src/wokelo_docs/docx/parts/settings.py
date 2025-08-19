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
|SettingsPart| and closely related objects
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from ..opc.constants import CONTENT_TYPE as CT
from ..opc.packuri import PackURI
from ..opc.part import XmlPart
from ..oxml import parse_xml
from ..settings import Settings


class SettingsPart(XmlPart):
    """
    Document-level settings part of a WordprocessingML (WML) package.
    """
    @classmethod
    def default(cls, package):
        """
        Return a newly created settings part, containing a default
        `w:settings` element tree.
        """
        partname = PackURI('/word/settings.xml')
        content_type = CT.WML_SETTINGS
        element = parse_xml(cls._default_settings_xml())
        return cls(partname, content_type, element, package)

    @property
    def settings(self):
        """
        A |Settings| proxy object for the `w:settings` element in this part,
        containing the document-level settings for this document.
        """
        return Settings(self.element)

    @classmethod
    def _default_settings_xml(cls):
        """
        Return a bytestream containing XML for a default settings part.
        """
        path = os.path.join(
            os.path.split(__file__)[0], '..', 'templates',
            'default-settings.xml'
        )
        with open(path, 'rb') as f:
            xml_bytes = f.read()
        return xml_bytes

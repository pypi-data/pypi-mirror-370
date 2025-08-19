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



"""lxml custom element classes for theme-related XML elements."""

from __future__ import annotations

from . import parse_from_template
from .xmlchemy import BaseOxmlElement


class CT_OfficeStyleSheet(BaseOxmlElement):
    """
    ``<a:theme>`` element, root of a theme part
    """

    _tag_seq = (
        "a:themeElements",
        "a:objectDefaults",
        "a:extraClrSchemeLst",
        "a:custClrLst",
        "a:extLst",
    )
    del _tag_seq

    @classmethod
    def new_default(cls):
        """
        Return a new ``<a:theme>`` element containing default settings
        suitable for use with a notes master.
        """
        return parse_from_template("theme")

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



"""|ChartFormat| and related objects.

|ChartFormat| acts as proxy for the `spPr` element, which provides visual shape properties such as
line and fill for chart elements.
"""

from __future__ import annotations

from pptx.dml.fill import FillFormat
from pptx.dml.line import LineFormat
from pptx.shared import ElementProxy
from pptx.util import lazyproperty


class ChartFormat(ElementProxy):
    """
    The |ChartFormat| object provides access to visual shape properties for
    chart elements like |Axis|, |Series|, and |MajorGridlines|. It has two
    properties, :attr:`fill` and :attr:`line`, which return a |FillFormat|
    and |LineFormat| object respectively. The |ChartFormat| object is
    provided by the :attr:`format` property on the target axis, series, etc.
    """

    @lazyproperty
    def fill(self):
        """
        |FillFormat| instance for this object, providing access to fill
        properties such as fill color.
        """
        spPr = self._element.get_or_add_spPr()
        return FillFormat.from_fill_parent(spPr)

    @lazyproperty
    def line(self):
        """
        The |LineFormat| object providing access to the visual properties of
        this object, such as line color and line style.
        """
        spPr = self._element.get_or_add_spPr()
        return LineFormat(spPr)

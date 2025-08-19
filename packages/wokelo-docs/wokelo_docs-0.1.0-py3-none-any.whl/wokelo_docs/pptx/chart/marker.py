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



"""Marker-related objects.

Only the line-type charts Line, XY, and Radar have markers.
"""

from __future__ import annotations

from pptx.dml.chtfmt import ChartFormat
from pptx.shared import ElementProxy
from pptx.util import lazyproperty


class Marker(ElementProxy):
    """
    Represents a data point marker, such as a diamond or circle, on
    a line-type chart.
    """

    @lazyproperty
    def format(self):
        """
        The |ChartFormat| instance for this marker, providing access to shape
        properties such as fill and line.
        """
        marker = self._element.get_or_add_marker()
        return ChartFormat(marker)

    @property
    def size(self):
        """
        An integer between 2 and 72 inclusive indicating the size of this
        marker in points. A value of |None| indicates no explicit value is
        set and the size is inherited from a higher-level setting or the
        PowerPoint default (which may be 9). Assigning |None| removes any
        explicitly assigned size, causing this value to be inherited.
        """
        marker = self._element.marker
        if marker is None:
            return None
        return marker.size_val

    @size.setter
    def size(self, value):
        marker = self._element.get_or_add_marker()
        marker._remove_size()
        if value is None:
            return
        size = marker._add_size()
        size.val = value

    @property
    def style(self):
        """
        A member of the :ref:`XlMarkerStyle` enumeration indicating the shape
        of this marker. Returns |None| if no explicit style has been set,
        which corresponds to the "Automatic" option in the PowerPoint UI.
        """
        marker = self._element.marker
        if marker is None:
            return None
        return marker.symbol_val

    @style.setter
    def style(self, value):
        marker = self._element.get_or_add_marker()
        marker._remove_symbol()
        if value is None:
            return
        symbol = marker._add_symbol()
        symbol.val = value

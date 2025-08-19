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



"""Abstract types used by `python-pptx`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Protocol

if TYPE_CHECKING:
    from pptx.opc.package import XmlPart
    from pptx.util import Length


class ProvidesExtents(Protocol):
    """An object that has width and height."""

    @property
    def height(self) -> Length:
        """Distance between top and bottom extents of shape in EMUs."""
        ...

    @property
    def width(self) -> Length:
        """Distance between left and right extents of shape in EMUs."""
        ...


class ProvidesPart(Protocol):
    """An object that provides access to its XmlPart.

    This type is for objects that need access to their part, possibly because they need access to
    the package or related parts.
    """

    @property
    def part(self) -> XmlPart: ...

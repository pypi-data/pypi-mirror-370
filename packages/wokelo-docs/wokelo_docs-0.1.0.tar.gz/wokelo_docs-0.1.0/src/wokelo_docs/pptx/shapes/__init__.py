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



"""Objects used across sub-package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pptx.opc.package import XmlPart
    from pptx.types import ProvidesPart


class Subshape(object):
    """Provides access to the containing part for drawing elements that occur below a shape.

    Access to the part is required for example to add or drop a relationship. Provides
    `self._parent` attribute to subclasses.
    """

    def __init__(self, parent: ProvidesPart):
        super(Subshape, self).__init__()
        self._parent = parent

    @property
    def part(self) -> XmlPart:
        """The package part containing this object."""
        return self._parent.part

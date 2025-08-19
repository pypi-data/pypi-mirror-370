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
Objects related to shapes, visual objects that appear on the drawing layer of
a document.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .enum.shape import WD_INLINE_SHAPE
from .oxml.ns import nsmap
from .shared import Parented


class InlineShapes(Parented):
    """
    Sequence of |InlineShape| instances, supporting len(), iteration, and
    indexed access.
    """
    def __init__(self, body_elm, parent):
        super(InlineShapes, self).__init__(parent)
        self._body = body_elm

    def __getitem__(self, idx):
        """
        Provide indexed access, e.g. 'inline_shapes[idx]'
        """
        try:
            inline = self._inline_lst[idx]
        except IndexError:
            msg = "inline shape index [%d] out of range" % idx
            raise IndexError(msg)
        return InlineShape(inline)

    def __iter__(self):
        return (InlineShape(inline) for inline in self._inline_lst)

    def __len__(self):
        return len(self._inline_lst)

    @property
    def _inline_lst(self):
        body = self._body
        xpath = '//w:p/w:r/w:drawing/wp:inline'
        return body.xpath(xpath)


class InlineShape(object):
    """
    Proxy for an ``<wp:inline>`` element, representing the container for an
    inline graphical object.
    """
    def __init__(self, inline):
        super(InlineShape, self).__init__()
        self._inline = inline

    @property
    def height(self):
        """
        Read/write. The display height of this inline shape as an |Emu|
        instance.
        """
        return self._inline.extent.cy

    @height.setter
    def height(self, cy):
        self._inline.extent.cy = cy
        self._inline.graphic.graphicData.pic.spPr.cy = cy

    @property
    def type(self):
        """
        The type of this inline shape as a member of
        ``docx.enum.shape.WD_INLINE_SHAPE``, e.g. ``LINKED_PICTURE``.
        Read-only.
        """
        graphicData = self._inline.graphic.graphicData
        uri = graphicData.uri
        if uri == nsmap['pic']:
            blip = graphicData.pic.blipFill.blip
            if blip.link is not None:
                return WD_INLINE_SHAPE.LINKED_PICTURE
            return WD_INLINE_SHAPE.PICTURE
        if uri == nsmap['c']:
            return WD_INLINE_SHAPE.CHART
        if uri == nsmap['dgm']:
            return WD_INLINE_SHAPE.SMART_ART
        return WD_INLINE_SHAPE.NOT_IMPLEMENTED

    @property
    def width(self):
        """
        Read/write. The display width of this inline shape as an |Emu|
        instance.
        """
        return self._inline.extent.cx

    @width.setter
    def width(self, cx):
        self._inline.extent.cx = cx
        self._inline.graphic.graphicData.pic.spPr.cx = cx

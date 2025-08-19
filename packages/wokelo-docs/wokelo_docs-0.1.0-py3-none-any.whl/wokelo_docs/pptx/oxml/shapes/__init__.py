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



"""Base shape-related objects such as BaseShape."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from pptx.oxml.shapes.autoshape import CT_Shape
    from pptx.oxml.shapes.connector import CT_Connector
    from pptx.oxml.shapes.graphfrm import CT_GraphicalObjectFrame
    from pptx.oxml.shapes.groupshape import CT_GroupShape
    from pptx.oxml.shapes.picture import CT_Picture


ShapeElement: TypeAlias = (
    "CT_Connector | CT_GraphicalObjectFrame |  CT_GroupShape | CT_Picture | CT_Shape"
)

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

"""Block item container, used by body, cell, header, etc.

Block level items are things like paragraph and table, although there are a few other
specialized ones like structured document tags.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from wokelo_docs.docx.oxml.table import CT_Tbl
from wokelo_docs.docx.oxml.ns import  qn
from wokelo_docs.docx.shared import Parented
from wokelo_docs.docx.text.paragraph import Paragraph
from wokelo_docs.docx.api import element

class BlockItemContainer(Parented):
    """Base class for proxy objects that can contain block items.

    These containers include _Body, _Cell, header, footer, footnote, endnote, comment,
    and text box objects. Provides the shared functionality to add a block item like
    a paragraph or table.
    """

    def __init__(self, element, parent):
        super(BlockItemContainer, self).__init__(parent)
        self._element = element

    def add_paragraph(self, text='', style=None):
        """
        Return a paragraph newly added to the end of the content in this
        container, having *text* in a single run if present, and having
        paragraph style *style*. If *style* is |None|, no paragraph style is
        applied, which has the same effect as applying the 'Normal' style.
        """
        paragraph = self._add_paragraph()
        if text:
            paragraph.add_run(text)
        if style is not None:
            paragraph.style = style
        return paragraph

    def add_table(self, rows, cols, width):
        """
        Return a table of *width* having *rows* rows and *cols* columns,
        newly appended to the content in this container. *width* is evenly
        distributed between the table columns.
        """
        from .table import Table
        tbl = CT_Tbl.new_tbl(rows, cols, width)
        self._element._insert_tbl(tbl)
        return Table(tbl, self)

    @property
    def paragraphs(self):
        """
        A list containing the paragraphs in this container, in document
        order. Read-only.
        """
        return [Paragraph(p, self) for p in self._element.p_lst]

    @property
    def tables(self):
        """
        A list containing the tables in this container, in document order.
        Read-only.
        """
        from .table import Table
        return [Table(tbl, self) for tbl in self._element.tbl_lst]
    @property
    def elements(self):
        """
        A list containing the elements in this container (paragraph and tables), in document order.
        """
        return [element(item,self.part) for item in self._element.getchildren()]
    
    
    @property
    def abstractNumIds(self):
        return [numId for numId in self.part.numbering_part.element.iterchildren(qn('w:abstractNum'))]

    
    def _add_paragraph(self):
        """
        Return a paragraph newly added to the end of the content in this
        container.
        """
        return Paragraph(self._element.add_p(), self)


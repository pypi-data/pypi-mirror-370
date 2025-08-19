# Copyright (c) 2013 Steve Canny, https://github.com/scanny
# Copyright (c) 2025 Wokelo, https://github.com/Wokelo-AI/wokelo-docs
#
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# This file contains original code licensed under the MIT License
# and modifications licensed under the Apache License, Version 2.0.
#
# Original code is licensed under the MIT License:
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
# Modifications are licensed under the Apache License, Version 2.0:
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See LICENSE in the project root for full license information.



# encoding: utf-8

"""|DocumentPart| and closely related objects"""

from __future__ import absolute_import, division, print_function, unicode_literals

from wokelo_docs.docx.document import Document
from wokelo_docs.docx.opc.constants import RELATIONSHIP_TYPE as RT
from wokelo_docs.docx.parts.hdrftr import FooterPart, HeaderPart
from wokelo_docs.docx.parts.numbering import NumberingPart
from wokelo_docs.docx.parts.settings import SettingsPart
from wokelo_docs.docx.parts.story import BaseStoryPart
from wokelo_docs.docx.parts.styles import StylesPart
from wokelo_docs.docx.parts.comments import CommentsPart
from wokelo_docs.docx.parts.footnotes import FootnotesPart
from wokelo_docs.docx.shape import InlineShapes
from wokelo_docs.docx.shared import lazyproperty
from pptx.parts.chart import ChartPart
from wokelo_docs.docx.oxml.shape import CT_Inline

class DocumentPart(BaseStoryPart):
    """Main document part of a WordprocessingML (WML) package, aka a .docx file.

    Acts as broker to other parts such as image, core properties, and style parts. It
    also acts as a convenient delegate when a mid-document object needs a service
    involving a remote ancestor. The `Parented.part` property inherited by many content
    objects provides access to this part object for that purpose.
    """

    def add_footer_part(self):
        """Return (footer_part, rId) pair for newly-created footer part."""
        footer_part = FooterPart.new(self.package)
        rId = self.relate_to(footer_part, RT.FOOTER)
        return footer_part, rId

    def add_header_part(self):
        """Return (header_part, rId) pair for newly-created header part."""
        header_part = HeaderPart.new(self.package)
        rId = self.relate_to(header_part, RT.HEADER)
        return header_part, rId

    @property
    def core_properties(self):
        """
        A |CoreProperties| object providing read/write access to the core
        properties of this document.
        """
        return self.package.core_properties

    @property
    def document(self):
        """
        A |Document| object providing access to the content of this document.
        """
        return Document(self._element, self)

    def drop_header_part(self, rId):
        """Remove related header part identified by *rId*."""
        self.drop_rel(rId)

    def footer_part(self, rId):
        """Return |FooterPart| related by *rId*."""
        return self.related_parts[rId]

    def get_or_add_chart(self, chart_type, x, y, cx, cy, chart_data):
        """
        Return an (rId, chart) 2-tuple for the chart.
        Access the chart properties like description in python-pptx documents.
        """
        chart_part = ChartPart.new(chart_type, chart_data, self.package)
        rId = self.relate_to(chart_part, RT.CHART)
        return rId, chart_part.chart


    def get_style(self, style_id, style_type):
        """
        Return the style in this document matching *style_id*. Returns the
        default style for *style_type* if *style_id* is |None| or does not
        match a defined style of *style_type*.
        """
        return self.styles.get_by_id(style_id, style_type)

    def get_style_id(self, style_or_name, style_type):
        """
        Return the style_id (|str|) of the style of *style_type* matching
        *style_or_name*. Returns |None| if the style resolves to the default
        style for *style_type* or if *style_or_name* is itself |None|. Raises
        if *style_or_name* is a style of the wrong type or names a style not
        present in the document.
        """
        return self.styles.get_style_id(style_or_name, style_type)

    def header_part(self, rId):
        """Return |HeaderPart| related by *rId*."""
        return self.related_parts[rId]

    def new_chart_inline(self, chart_type, x, y, cx, cy, chart_data):
        """
        Return a newly-created `w:inline` element containing the chart
        with position *x* and *y* and width *cx* and height *y*
        """
        rId, chart = self.get_or_add_chart(chart_type, x, y, cx, cy, chart_data)
        shape_id = self.next_id
        return CT_Inline.new_chart_inline(shape_id, rId, x, y, cx, cy), chart



    @lazyproperty
    def inline_shapes(self):
        """
        The |InlineShapes| instance containing the inline shapes in the
        document.
        """
        return InlineShapes(self._element.body, self)

    @lazyproperty
    def numbering_part(self):
        """
        A |NumberingPart| object providing access to the numbering
        definitions for this document. Creates an empty numbering part if one
        is not present.
        """
        try:
            return self.part_related_by(RT.NUMBERING)
        except KeyError:
            numbering_part = NumberingPart.new()
            self.relate_to(numbering_part, RT.NUMBERING)
            return numbering_part
    
    

    def save(self, path_or_stream):
        """
        Save this document to *path_or_stream*, which can be either a path to
        a filesystem location (a string) or a file-like object.
        """
        self.package.save(path_or_stream)

    @property
    def settings(self):
        """
        A |Settings| object providing access to the settings in the settings
        part of this document.
        """
        return self._settings_part.settings

    @property
    def styles(self):
        """
        A |Styles| object providing access to the styles in the styles part
        of this document.
        """
        return self._styles_part.styles

    @property
    def _settings_part(self):
        """
        A |SettingsPart| object providing access to the document-level
        settings for this document. Creates a default settings part if one is
        not present.
        """
        try:
            return self.part_related_by(RT.SETTINGS)
        except KeyError:
            settings_part = SettingsPart.default(self.package)
            self.relate_to(settings_part, RT.SETTINGS)
            return settings_part

    @property
    def _styles_part(self):
        """
        Instance of |StylesPart| for this document. Creates an empty styles
        part if one is not present.
        """
        try:
            return self.part_related_by(RT.STYLES)
        except KeyError:
            styles_part = StylesPart.default(self.package)
            self.relate_to(styles_part, RT.STYLES)
            return styles_part
    
    @lazyproperty
    def comments_part(self):
        """
        A |Comments| object providing read/write access to the core
        properties of this document.
        """
        # return self.package._comments_part

    @property
    def _comments_part(self):
        try:
            return self.part_related_by(RT.COMMENTS)
        except KeyError:
            comments_part = CommentsPart.default(self) 
            self.relate_to(comments_part, RT.COMMENTS)
            return comments_part
    
    @property
    def _footnotes_part(self):
        """
        |FootnotesPart| object related to this package. Creates
        a default Comments part if one is not present.
        """
        try:
            return self.part_related_by(RT.FOOTNOTES)
        except KeyError:
            footnotes_part = FootnotesPart.default(self)
            self.relate_to(footnotes_part, RT.FOOTNOTES)
            return  footnotes_part
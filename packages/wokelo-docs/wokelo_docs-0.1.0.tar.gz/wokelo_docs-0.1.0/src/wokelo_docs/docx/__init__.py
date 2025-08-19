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

from wokelo_docs.docx.api import Document  # noqa

__version__ = '0.2.20' 


# register custom Part classes with opc package reader

from wokelo_docs.docx.opc.constants import CONTENT_TYPE as CT, RELATIONSHIP_TYPE as RT
from wokelo_docs.docx.opc.part import PartFactory
from wokelo_docs.docx.opc.parts.coreprops import CorePropertiesPart

from wokelo_docs.docx.parts.document import DocumentPart
from wokelo_docs.docx.parts.hdrftr import FooterPart, HeaderPart
from wokelo_docs.docx.parts.image import ImagePart
from wokelo_docs.docx.parts.numbering import NumberingPart
from wokelo_docs.docx.parts.settings import SettingsPart
from wokelo_docs.docx.parts.styles import StylesPart
from wokelo_docs.docx.parts.comments import CommentsPart
from wokelo_docs.docx.parts.footnotes import FootnotesPart


def part_class_selector(content_type, reltype):
    if reltype == RT.IMAGE:
        return ImagePart
    return None


PartFactory.part_class_selector = part_class_selector
PartFactory.part_type_for[CT.WML_COMMENTS] = CommentsPart
PartFactory.part_type_for[CT.OPC_CORE_PROPERTIES] = CorePropertiesPart
PartFactory.part_type_for[CT.WML_DOCUMENT_MAIN] = DocumentPart
PartFactory.part_type_for[CT.WML_FOOTER] = FooterPart
PartFactory.part_type_for[CT.WML_HEADER] = HeaderPart
PartFactory.part_type_for[CT.WML_NUMBERING] = NumberingPart
PartFactory.part_type_for[CT.WML_SETTINGS] = SettingsPart
PartFactory.part_type_for[CT.WML_STYLES] = StylesPart
PartFactory.part_type_for[CT.WML_FOOTNOTES] = FootnotesPart

del (
    CT,
    CorePropertiesPart,
    DocumentPart,
    FooterPart,
    HeaderPart,
    FootnotesPart,
    CommentsPart,
    NumberingPart,
    PartFactory,
    SettingsPart,
    StylesPart,
    part_class_selector,
)

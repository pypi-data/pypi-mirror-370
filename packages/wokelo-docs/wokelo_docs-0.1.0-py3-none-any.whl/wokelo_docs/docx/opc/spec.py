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
Provides mappings that embody aspects of the Open XML spec ISO/IEC 29500.
"""

from .constants import CONTENT_TYPE as CT


default_content_types = (
    ('bin',     CT.PML_PRINTER_SETTINGS),
    ('bin',     CT.SML_PRINTER_SETTINGS),
    ('bin',     CT.WML_PRINTER_SETTINGS),
    ('bmp',     CT.BMP),
    ('emf',     CT.X_EMF),
    ('fntdata', CT.X_FONTDATA),
    ('gif',     CT.GIF),
    ('jpe',     CT.JPEG),
    ('jpeg',    CT.JPEG),
    ('jpg',     CT.JPEG),
    ('png',     CT.PNG),
    ('rels',    CT.OPC_RELATIONSHIPS),
    ('tif',     CT.TIFF),
    ('tiff',    CT.TIFF),
    ('wdp',     CT.MS_PHOTO),
    ('wmf',     CT.X_WMF),
    ('xlsx',    CT.SML_SHEET),
    ('xml',     CT.XML),
)

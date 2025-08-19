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
Provides objects that can characterize image streams as to content type and
size, as a required step in including them in a document.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from wokelo_docs.docx.image.bmp import Bmp
from wokelo_docs.docx.image.gif import Gif
from wokelo_docs.docx.image.jpeg import Exif, Jfif
from wokelo_docs.docx.image.png import Png
from wokelo_docs.docx.image.tiff import Tiff
from wokelo_docs.docx.image.emf import Emf

SIGNATURES = (
    # class, offset, signature_bytes
    (Png,  0, b'\x89PNG\x0D\x0A\x1A\x0A'),
    (Jfif, 6, b'JFIF'),
    (Exif, 6, b'Exif'),
    (Gif,  0, b'GIF87a'),
    (Gif,  0, b'GIF89a'),
    (Tiff, 0, b'MM\x00*'),  # big-endian (Motorola) TIFF
    (Tiff, 0, b'II*\x00'),  # little-endian (Intel) TIFF
    (Bmp,  0, b'BM'),
    (Emf,  40, b' EMF')
)

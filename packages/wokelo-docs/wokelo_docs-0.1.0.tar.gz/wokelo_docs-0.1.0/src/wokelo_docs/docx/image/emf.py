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

from __future__ import absolute_import, division, print_function

from .constants import MIME_TYPE
from .exceptions import InvalidImageStreamError
from .helpers import BIG_ENDIAN, StreamReader
from .image import BaseImageHeader
import struct

class Emf(BaseImageHeader):
    """
    Image header parser for PNG images
    """
    @property
    def content_type(self):
        """
        MIME content type for this image, unconditionally `image/png` for
        PNG images.
        """
        return MIME_TYPE.EMF

    @property
    def default_ext(self):
        """
        Default filename extension, always 'png' for PNG images.
        """
        return 'emf'

    @classmethod
    def from_stream(cls, stream,filename=None):
        """
        Return a |Emf| instance having header properties parsed from image in
        *stream*.
        """

        """
        @0 DWORD iType; // fixed
        @4 DWORD nSize; // var 
        @8 RECTL rclBounds;
        @24 RECTL rclFrame; // .01 millimeter units L T R B
        @40 DWORD dSignature; // ENHMETA_SIGNATURE = 0x464D4520
        DWORD nVersion;
        DWORD nBytes;
        DWORD nRecords;
        WORD  nHandles;
        WORD  sReserved;
        DWORD nDescription;
        DWORD offDescription;
        DWORD nPalEntries;
        SIZEL szlDevice;
        SIZEL szlMillimeters;
        """
        stream.seek(0)
        x = stream.read(40)
        stream.seek(0)
        iType,nSize = struct.unpack("ii",x[0:8])
        rclBounds = struct.unpack("iiii",x[8:24])
        rclFrame = struct.unpack("iiii",x[24:40])

        dpi = 300
        horz_dpi = dpi
        vert_dpi = dpi
        mmwidth = (rclFrame[2]-rclFrame[0])/100.0
        mmheight = (rclFrame[3]-rclFrame[1])/100.0
        px_width = int(mmwidth*dpi*0.03937008)
        px_height = int(mmheight*dpi*0.03937008)

        #1 dot/inch  =  0.03937008 pixel/millimeter
        return cls(px_width,px_height,horz_dpi,vert_dpi)
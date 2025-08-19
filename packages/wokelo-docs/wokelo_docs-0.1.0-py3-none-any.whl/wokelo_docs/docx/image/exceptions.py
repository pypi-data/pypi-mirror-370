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
Exceptions specific the the image sub-package
"""


class InvalidImageStreamError(Exception):
    """
    The recognized image stream appears to be corrupted
    """


class UnexpectedEndOfFileError(Exception):
    """
    EOF was unexpectedly encountered while reading an image stream.
    """


class UnrecognizedImageError(Exception):
    """
    The provided image stream could not be recognized.
    """

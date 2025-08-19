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
Provides Python 2/3 compatibility objects
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import sys

# ===========================================================================
# Python 3 versions
# ===========================================================================

if sys.version_info >= (3, 0):

    def cls_method_fn(cls, method_name):
        """
        Return the function object associated with the method of *cls* having
        *method_name*.
        """
        return getattr(cls, method_name)

    def is_string(obj):
        """
        Return True if *obj* is a string, False otherwise.
        """
        return isinstance(obj, str)

# ===========================================================================
# Python 2 versions
# ===========================================================================

else:

    def cls_method_fn(cls, method_name):
        """
        Return the function object associated with the method of *cls* having
        *method_name*.
        """
        unbound_method = getattr(cls, method_name)
        return unbound_method.__func__

    def is_string(obj):
        """
        Return True if *obj* is a string, False otherwise.
        """
        return isinstance(obj, basestring)

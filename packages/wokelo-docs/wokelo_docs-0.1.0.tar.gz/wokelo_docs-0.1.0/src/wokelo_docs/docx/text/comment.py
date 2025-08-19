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



from ..shared import Parented

class Comment(Parented):
    """[summary]

    :param Parented: [description]
    :type Parented: [type]
    """
    def __init__(self, com, parent):
        super(Comment, self).__init__(parent)
        self._com = self._element = self.element = com
    
    @property
    def paragraph(self):
        return self.element.paragraph
    
    @property
    def text(self):
        return self.element.paragraph.text
    
    @text.setter
    def text(self, text):
        self.element.paragraph.text = text
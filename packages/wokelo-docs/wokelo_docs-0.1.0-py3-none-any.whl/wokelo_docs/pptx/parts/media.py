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



"""MediaPart and related objects."""

from __future__ import annotations

import hashlib

from pptx.opc.package import Part
from pptx.util import lazyproperty


class MediaPart(Part):
    """A media part, containing an audio or video resource.

    A media part generally has a partname matching the regex
    `ppt/media/media[1-9][0-9]*.*`.
    """

    @classmethod
    def new(cls, package, media):
        """Return new |MediaPart| instance containing `media`.

        `media` must be a |Media| object.
        """
        return cls(
            package.next_media_partname(media.ext),
            media.content_type,
            package,
            media.blob,
        )

    @lazyproperty
    def sha1(self):
        """The SHA1 hash digest for the media binary of this media part.

        Example: `'1be010ea47803b00e140b852765cdf84f491da47'`
        """
        return hashlib.sha1(self._blob).hexdigest()

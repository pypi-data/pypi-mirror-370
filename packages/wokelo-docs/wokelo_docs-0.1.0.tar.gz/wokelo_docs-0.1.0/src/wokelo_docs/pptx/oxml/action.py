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



"""lxml custom element classes for text-related XML elements."""

from __future__ import annotations

from pptx.oxml.simpletypes import XsdString
from pptx.oxml.xmlchemy import BaseOxmlElement, OptionalAttribute


class CT_Hyperlink(BaseOxmlElement):
    """Custom element class for <a:hlinkClick> elements."""

    rId: str = OptionalAttribute("r:id", XsdString)  # pyright: ignore[reportAssignmentType]
    action: str | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "action", XsdString
    )

    @property
    def action_fields(self) -> dict[str, str]:
        """Query portion of the `ppaction://` URL as dict.

        For example `{'id':'0', 'return':'true'}` in 'ppaction://customshow?id=0&return=true'.

        Returns an empty dict if the URL contains no query string or if no action attribute is
        present.
        """
        url = self.action

        if url is None:
            return {}

        halves = url.split("?")
        if len(halves) == 1:
            return {}

        key_value_pairs = halves[1].split("&")
        return dict([pair.split("=") for pair in key_value_pairs])

    @property
    def action_verb(self) -> str | None:
        """The host portion of the `ppaction://` URL contained in the action attribute.

        For example 'customshow' in 'ppaction://customshow?id=0&return=true'. Returns |None| if no
        action attribute is present.
        """
        url = self.action

        if url is None:
            return None

        protocol_and_host = url.split("?")[0]
        host = protocol_and_host[11:]

        return host

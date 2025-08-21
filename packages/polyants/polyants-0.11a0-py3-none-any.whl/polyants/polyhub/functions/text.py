""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from __future__ import annotations

from typing import Union, Optional
from re import compile, Pattern


def substr_by_mask(
    text: Optional[str] = None, mask: Union[str, Pattern] = r'(.*)', group: int = 0
) -> Optional[Union[int | bytes | None]]:
    if isinstance(mask, str):
        mask = compile(mask)

    found = None
    if matched := mask.search(text):
        try:
            found = matched.groups(group)[0]
        except IndexError:
            pass

    return found

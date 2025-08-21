""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from json import loads
from jinja2 import Environment
from polyants.internal import log

JINJA = Environment()


def from_json(value, default='{}'):
    try:
        parsed = loads(value)
    except Exception as e:
        log.warning('Ошибка фильтра: %s при парсинге:\n%s', e, value)
        parsed = loads(default)

    return parsed


def to_type(value):
    return type(value)


JINJA.filters['from_json'] = from_json
JINJA.filters['to_type'] = to_type

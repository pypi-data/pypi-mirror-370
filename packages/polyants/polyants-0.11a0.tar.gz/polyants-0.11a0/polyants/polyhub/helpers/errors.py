""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Error:
    code: int
    message: str
    field: Optional[str] = None


msg = 'Одноименный объект в текущем контейнере уже существует'
CDNICU = Error(code=1010, message=msg)  # cloud, duplicate name in container, upload

msg = 'Не найден контейнер объекта'
CNCFU = Error(code=1020, message=msg)  # cloud, no container found, upload

msg = 'Не выбран объект загрузки'
CNOSU = Error(code=1030, message=msg)  # cloud, no object selected, upload

msg = 'Ошибка загрузки в контейнер'
CU = Error(code=1000, message=msg)  # cloud, upload

msg = 'Ошибка перемещения объекта'
CM = Error(code=1100, message=msg)  # cloud, move

msg = 'Одноименный объект в родительском контейнере уже существует'
CDNICM = Error(code=1110, message=msg)  # cloud, duplicate name in container, move

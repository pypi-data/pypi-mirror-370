""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import logging
import datetime

from typing import Callable
from traceback import format_tb
from importlib import import_module
from polyants.polyhub.enums import GenericState, ObjectType


def get_now(format_=None, utc=False):
    """Возвращает текущую дату и время, с учетом формата, если задан.
    Пример формата: `%Y-%m-%dT%H:%M:%S`
    """
    now = datetime.datetime.now(datetime.UTC) if utc else datetime.datetime.now()
    return now.strftime(format_) if format_ else now


def get_object_class_type(cls) -> ObjectType:
    """Возвращает тип объекта на основе класса."""
    return ObjectType[cls.__name__.upper()]


def get_type_object_class(type_: ObjectType) -> str:
    """Возвращает наименование класса объекта на основании его типа."""
    return ObjectType(type_).name.capitalize()  # pyre-ignore[16]


def get_object_type(object_, type_=None) -> ObjectType:
    """Возвращает тип объекта."""
    return type_ or get_object_class_type(object_.__class__)


def get_object_class(object_) -> str:
    """Возвращает наименование класса объекта."""
    type_ = get_object_type(object_)
    return get_type_object_class(type_)


def get_active_state(state_enum=GenericState):
    return state_enum.ACTIVE & ~state_enum.DELETED


def is_object_active(object_, state_enum=GenericState):
    return object_.state & (state_enum.DELETED | state_enum.ACTIVE) == state_enum.ACTIVE


def log_traceback(error, logger=None, prefix=''):
    result = error
    logger = logger or logging.getLogger()

    if isinstance(error, Exception) and logger.getEffectiveLevel() == logging.DEBUG:
        tb = ''.join(format_tb(error.__traceback__))

        result = f'{prefix}{error}\n{tb}'
    elif error:
        result = f'{prefix}{error.__class__.__name__}: {error}'

    return result


def import_by_path(target_path: str | Callable) -> Callable:
    """Импортирует объекты из модуля по переданному пути."""
    if isinstance(target_path, str):
        module_name, target_name = target_path.rsplit('.', 1)
        module = import_module(module_name)

        return getattr(module, target_name)

    return target_path


def get_definitions(definitions: dict, type_: str):
    """Возвращает объекты оркестратора из словаря с ключами, их группирующими."""
    result = None
    defined = list()
    for v in definitions.values():
        if items := v.get(type_):
            defined.extend([import_by_path(i) for i in items])

    if defined:
        result = defined

    return result

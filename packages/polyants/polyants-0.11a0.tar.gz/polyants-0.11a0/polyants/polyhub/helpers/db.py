""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import psycopg2

from typing import Optional
from dataclasses import dataclass
from polyants.polyhub.constants import DWASH_SCHEMA
from polyants.polyhub.exceptions import DBException, ProviderException
from polyants.polyhub.enums import ProviderType
from polyants.polyhub.helpers.crypto import decrypt, get_app_secret
from polyants.internal import log


@dataclass
class Provider:
    id: str
    type: ProviderType
    host: str
    schema: str
    db: str
    login: str
    password: str
    port: int
    options: dict


def get_connection(connection=None):
    if connection is None:
        conn_string = get_app_secret('DATABASE_URL', with_env=True)
        if conn_string:
            connection = psycopg2.connect(conn_string)
        else:
            raise ProviderException('Подключение к БД не найдено')

    return connection


def execute_function(
    name, parameters=None, singular=False, default=None, log_errors=True, schema=DWASH_SCHEMA, connection=None
):
    """Выполняет (select) функции и возвращает  результат."""
    parameters = parameters or list()
    connection = get_connection(connection=connection)
    name = f'{schema}.{name}' if schema else name

    try:
        cursor = connection.cursor()
        cursor.callproc(name, parameters)
        result = list(cursor.fetchall())
        cursor.close()
        connection.commit()
    except Exception as e:
        connection.rollback()
        if log_errors:
            log.warning(f'Ошибка выполнения функции {name}, параметры: {parameters}')
        raise DBException(f'Ошибка серверной функции: {e}')
    finally:
        connection.close()

    if singular:
        if result and len(result) == 1:
            result = result[-1][-1]
        elif not default:
            count = len(result) if result else 'ни одного'
            msg = f'Функция {name} вернула элементов: {count}. Ожидался 1.'
            if log_errors:
                log.error(msg)
            raise DBException(msg)

    return result


def call_procedure(name, params=None, schema=DWASH_SCHEMA):
    """Вызывает (call) процедуры не имеющие возвращаемых параметров.
    Формат параметров: [(value, type), ]
    """
    name = f'{schema}.{name}' if schema else name
    connection = get_connection()
    params = params or list()
    params_template = ','.join((f'%s::{t}' for _, t in params))
    query = f'call {name}({params_template})'

    try:
        cursor = connection.cursor()
        cursor.execute(query, [v for v, _ in params])
        cursor.close()
        connection.commit()
    except Exception as e:
        connection.rollback()
        log.error(f'Ошибка вызова процедуры {name} ({params}): {e}')
        raise DBException(f'Ошибка серверной процедуры: {e}')
    finally:
        connection.close()


def get_provider(user_id: Optional[str] = None, provider_id: Optional[str] = None, provider: Optional[dict] = None):
    result = None

    if not provider_id and provider:
        provider_id = provider.get('id')
        provider_code = provider.get('code')
    else:
        provider_code = None

    if provider_id or provider_code:
        provider = provider_code or provider_id
        parameters = [user_id, provider_id, provider_code]
        found = execute_function('outer_get_provider', parameters=parameters)

        if found:
            if len(found) != 1:
                raise ProviderException(f'Провайдер {provider} не определен однозначно')
            else:
                r = found[0]
                result = Provider(
                    id=r[0],
                    type=ProviderType[r[1]],
                    host=r[2],
                    schema=r[3],
                    db=r[4],
                    login=r[5],
                    password=decrypt(r[6]),
                    port=r[7],
                    options=r[8],
                )
        else:
            raise ProviderException(f'Провайдер {provider} не найден')

    return result

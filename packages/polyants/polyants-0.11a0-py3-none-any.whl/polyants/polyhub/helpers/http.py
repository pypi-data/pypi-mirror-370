""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import httpx
import urllib.parse

from functools import cache
from socket import gethostname, gethostbyname
from json import JSONDecodeError
from polyants.internal import log
from polyants.polyhub.exceptions import HttpException
from polyants.polyhub.constants import APP_CODE, BACK_CODE, API_PORT
from polyants.polyhub.helpers.grpcapi import get_protocol as grpc_get_protocol


@cache
def get_protocol():
    return grpc_get_protocol()


@cache
def get_host_name():
    return gethostname()


@cache
def get_host_by_name(name):
    return gethostbyname(name)


@cache
def get_service_code(hostname=None):
    hostname = hostname or get_host_name()
    return hostname.lstrip(f'{APP_CODE}-')


def build_url(base='', slug='', **params):
    """Склеивает url из двух частей и параметров.
    В параметрах не поддерживает повторяющиеся ключи и ключ `slug`.
    """
    url_parts = list(urllib.parse.urlparse(base))

    if slug:
        url_parts[2] = slug if slug.startswith('/') else f"{url_parts[2].rstrip('/')}/{slug}"

    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def get_parsed_url(url):
    return urllib.parse.urlparse(url)


def get_url_slug(url):
    parts = list(urllib.parse.urlparse(url))
    path = parts[2].strip('/')

    query = f'?{parts[4]}' if parts[4] else ''

    return f"/{path}{query}"


def request(method, url, json=None, data=None, auth=None, ssl_verify=True, expect_ok=True, headers=None):
    """Выполняет http запрос.
    expect_ok - при False не вызывать исключение при неуспешном запросе, а возвращать ответ.
    """
    log.debug(f'{method} запрос к {url}')

    with httpx.Client(verify=ssl_verify) as client:
        try:
            r = client.request(method, url, auth=auth, json=json, data=data, headers=headers)
        except httpx.RequestError as e:
            raise HttpException(f'Ошибка {method} запроса к {url}: {e}')

    log.debug(f'Ответ (статус {r.status_code}): {r.text}')

    if expect_ok and r.is_error:
        raise HttpException(f'{method} запрос к {url} вернул {r.status_code}: {r.text}')

    return r


def is_json_response(response: httpx.Response):
    if (ct := response.headers.get('Content-Type')) and 'json' in ct.lower():
        return True

    return False


def get_response_data(r):
    result = r.text
    if is_json_response(r):
        try:
            result = r.json()
        except JSONDecodeError:
            pass

    return result


def get_api_host_url(host):
    if host == BACK_CODE:
        url = f'{get_protocol()}://{APP_CODE}-{BACK_CODE}:{API_PORT}'
    else:
        url = f'http://{APP_CODE}-{host}:{API_PORT}'

    return url

""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import re
import requests

from abc import ABCMeta, abstractmethod
from datetime import timedelta
from polyants.internal import log
from polyants.polyhub.helpers.common import get_now
from polyants.polyhub.helpers.http import build_url
from polyants.polyhub.exceptions import ViApiException

re_units = {
    'viqube': re.compile(r'\/?viqube\/.+', flags=re.RegexFlag.IGNORECASE),
    'dc': re.compile(r'\/?datacollection\/.+', flags=re.RegexFlag.IGNORECASE),
}


def get_unit(url, strict=True):
    for k, v in re_units.items():
        if v.match(url):
            unit = k
            break
    else:
        if strict:
            raise ViApiException(f'Неизвестный тип запроса Visiology: {url}')

    return unit


class BaseHook(metaclass=ABCMeta):
    """Класс взаимодействия с API сервиса Visiology."""

    generation = None

    def __init__(self, provider, **kwargs):
        """Инициализация параметров подключения"""
        self._ssl_verify = None
        self._configuration = None
        self.provider = provider
        options = provider.options or dict()
        self.batch = options.get('batch', 10000)
        self.pool = options.get('pool', 10)
        self._context = {
            'user': provider.login,
            'pass': provider.password,
            'url': provider.host,
            'options': options,
        }

        self.conn = self._get_conn()
        self.connected = False

    @property
    def token(self):
        if self._is_token_expired():
            self.conn = self._get_conn()

        return self.conn['token']

    @property
    def auth_string(self):
        if self._is_token_expired():
            self.conn = self._get_conn()

        return f"{self.conn['token_type']} {self.conn['token']}"

    @property
    def ssl_verify(self):
        if self._ssl_verify is None:
            self._ssl_verify = self._context['options'].get('ssl_verify', True)

        return self._ssl_verify

    @property
    @abstractmethod
    def configuration(self):
        """Параметры сервиса."""

    @abstractmethod
    def _update_headers(self, extra_headers=None):
        """Подготавливает хидеры для запроса."""

    @abstractmethod
    def _get_token(self):
        """Возвращает активный токен."""

    def _is_token_expired(self):
        return get_now() >= self.conn['token_expires']

    def _get_token_expires(self, token):
        return get_now() + timedelta(seconds=token['expires_in'])

    def _request_token(self, url, headers, data):
        try:
            r = requests.post(url=url, headers=headers, data=data, verify=self.ssl_verify)
        except Exception as e:
            raise ViApiException(f'Ошибка получения токена:\n{e}')

        if r.status_code == requests.codes.ok:
            token = r.json()
        else:
            answer = self._parse_response(r)
            msg = f'Http ошибка при полученнии токена: {r.status_code}, ответ:\n{answer}'
            raise ViApiException(msg)

        return token

    def _request(self, method, url, headers=None, data=None):
        try:
            self.connected = True
            r = requests.request(method, url, headers=headers, json=data)
            self.connected = False
        except Exception as e:
            headers['Authorization'] = '*******'
            raise ViApiException(f'{method.upper()} [{url}], хидеры:\n{headers}\nошибка:\n{e}')

        return r

    def _parse_response(self, response):
        content_type = response.headers.get('Content-Type')
        if content_type and response.text and 'application/json' in content_type:
            result = response.json()
        else:
            result = response.text
        return result

    def _get_conn(self):
        """Возвращает необходимые параметры подключения,
        включая действующий токен, в виде словаря.
        Обязательный набор:
            {
                "token": "active_access_token",
                "token_type": "Bearer",
                "token_expires": 600
            }
        """
        conn = dict()
        conn['entry_point'] = self._context['url']

        token = self._get_token()
        conn['token'] = token['access_token']
        conn['token_type'] = token['token_type']
        conn['token_expires'] = self._get_token_expires(token)

        return conn

    def call(self, resource, method='post', extra_headers=None, data=None):
        """Универсальный вызов API.
        Args:
            :resource - адрес ресурса относительно API entry point
            :method - тип сообщения, обычно get или post
            :extra_headers - http заголовки, дополняющие, либо переопределяющие стандартные
            :data - полезная нагрузка запроса, как правило - словарь
        Returns:
            Ответ сервера, как правило - в виде словаря
        """
        headers = self._update_headers(extra_headers)

        url = build_url(self._context['url'], resource)

        if self._is_token_expired():
            # обновляем токен по времени
            self.conn = self._get_conn()
            headers = self._update_headers(extra_headers)

        r = self._request(method, url, headers=headers, data=data)
        answer = self._parse_response(r)

        if r.status_code == requests.codes.forbidden and 'token expired' in answer:  # @UndefinedVariable
            # пытаемся обновить токен по ошибке
            self.conn = self._get_conn()
            headers = self._update_headers(extra_headers)

            r = self._request(method, url, headers=headers, data=data)
            answer = self._parse_response(r)

        if r.status_code != requests.codes.ok:  # @UndefinedVariable
            data = f'\nтело:\n{data}' if data is not None else ''
            msg = f'{method.upper()} [{url}], код ошибки: {r.status_code}, ответ:\n{answer}{data}'
            raise ViApiException(msg)

        return answer

    def disconnect(self):
        self.connected = False


class HookV3(BaseHook):
    generation = 3

    @property
    def configuration(self):
        if self._configuration is None:
            host = self._context['url']
            self._configuration = {
                "dashboardServiceUrl": build_url(host, 'dashboard-service'),
                "workspaceServiceUrl": build_url(host, 'workspace-service'),
                "dashboardViewerUrl": build_url(host, 'dashboard-viewer'),
                "authorityUrl": build_url(host, 'keycloak/realms/Visiology'),
                "exportDashboardTimeout": 600,
                "exportWidgetDataTimeout": 600,
                "maxWidgetDataExcelRows": 10000,
            }
            url = build_url(self._context['url'], 'dashboard-viewer/configuration')
            try:
                r = requests.get(url=url, verify=self.ssl_verify)
            except Exception as e:
                log.warning('Ошибка получения конфигурации API:\n%s', e)
            else:
                if r.status_code == requests.codes.ok:
                    self._configuration.update(r.json())

        return self._configuration

    def _update_headers(self, extra_headers=None):
        headers = {'Content-Type': 'application/json', 'Authorization': self.auth_string}

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _get_token(self):
        ctx = self._context
        auth_url = self.configuration['authorityUrl'].strip('/')
        url = f'{auth_url}/protocol/openid-connect/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        grant_type = ctx['options'].get('grant_type', 'client_credentials')
        params = {'grant_type': grant_type, 'client_id': ctx['user'] or 'visiology_m2m', 'client_secret': ctx['pass']}
        if scope := ctx['options'].get('scope'):
            params['scope'] = scope

        return self._request_token(url, headers, params)


class Hook(BaseHook):
    generation = 2

    def __init__(self, provider, **kwargs):
        """Инициализация параметров подключения"""
        self._api_version = None
        self._unit = kwargs.pop('unit', 'viqube')
        super().__init__(provider, **kwargs)

    @property
    def configuration(self):
        if self._configuration is None:
            self._configuration = dict()
            if self._unit == 'dash':
                self._configuration = {
                    'coreFacadeRelativeUri': 'corelogic',
                    'queryPath': 'api/query',
                    'viQubeCubeId': 'DB',
                }
                url = build_url(self._context['url'], 'viewer/GetConfiguration')
                try:
                    r = requests.get(url=url, verify=self.ssl_verify)
                except Exception as e:
                    log.warning('Ошибка получения конфигурации API:\n%s', e)
                else:
                    if r.status_code == requests.codes.ok:
                        self._configuration.update(r.json())

        return self._configuration

    @property
    def api_version(self):
        if self._api_version is None:
            self._api_version = ''

            if self._unit == 'viqube':
                # запрашиваем версию API у целевого сервиса
                url = build_url(self._context['url'], 'viqube/version')

                try:
                    r = requests.get(url=url, verify=self.ssl_verify)
                except Exception as e:
                    raise ViApiException(f'Ошибка получения версии API:\n{e}')

                if r.status_code == requests.codes.ok:  # @UndefinedVariable
                    self._api_version = r.json()['apiStable']
                else:
                    answer = self._parse_response(r)
                    msg = f'Http ошибка при полученнии версии API: код = {r.status_code}, ответ:\n{answer}'
                    raise ViApiException(msg)
            elif self._unit == 'dc':
                self._api_version = '1.0'

        return self._api_version

    def _update_headers(self, extra_headers=None):
        headers = {'Authorization': self.auth_string}

        if self.api_version:
            headers['X-API-VERSION'] = self.api_version

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _get_token(self):
        ctx = self._context
        scope_name = 'scopes'
        scope = ctx['options'].get('scopes')
        authorization = ctx['options'].get('authorization')

        if self._unit == 'viqube':
            scope = ctx['options'].get('scope', 'viqube_api viqubeadmin_api')
            scope_name = 'scope'
            authorization = authorization or 'Basic dmlxdWJlYWRtaW5fcm9fY2xpZW50OjcmZEo1UldwVVMkLUVVQE1reHU='
        elif self._unit == 'dc':
            scope = scope or 'viewer_api core_logic_facade'
        elif self._unit == 'dash':
            scope = scope or 'viqube_api viewer_api'
        elif 'scope' in ctx['options'] and 'scopes' not in ctx['options']:
            scope = ctx['options']['scope']
            scope_name = 'scope'
        else:
            unit_str = self._unit or 'без scope'
            raise ViApiException(f'API подсистемы Visiology <{unit_str}> не поддерживается')

        authorization = authorization or 'Basic cm8uY2xpZW50OmFtV25Cc3B9dipvfTYkSQ=='
        grant_type = ctx['options'].get('grant_type', 'password')
        response_type = ctx['options'].get('response_type', 'id_token token')

        params = {
            'grant_type': grant_type,
            scope_name: scope,
            'response_type': response_type,
            'username': ctx['user'],
            'password': ctx['pass'],
        }

        url = build_url(ctx['url'], 'idsrv/connect/token')

        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': authorization}

        return self._request_token(url, headers, params)


def get_hook(provider, **kwargs):
    hook_cls = Hook
    options = provider.options or dict()

    if generation := options.get('generation'):
        try:
            generation = int(generation)
        except ValueError:
            pass
        else:
            if generation == 3:
                hook_cls = HookV3
    else:
        host = provider.host.rstrip('/')
        if host.endswith('/v3'):
            hook_cls = HookV3
        else:
            if provider.login == 'visiology_m2m':
                hook_cls = HookV3

    return hook_cls(provider, **kwargs)

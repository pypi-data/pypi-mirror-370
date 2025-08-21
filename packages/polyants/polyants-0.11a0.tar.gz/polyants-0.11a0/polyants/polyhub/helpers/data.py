""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from typing import Union, Optional, Type
from pathlib import Path
from polyants.polyhub.constants import SQLITE_DIALECT
from polyants.polyhub.exceptions import DataException
from polyants.polyhub.enums import ProviderType
from polyants.polyhub.helpers.db import get_provider
from polyants.polyhub.helpers.sqlapi import Hook as SqlHook, get_querier
from polyants.polyhub.helpers.viapi import get_unit, Hook as ViHook
from polyants.polyhub.helpers.viasync import get_from_visiology


class Producer:
    def __init__(
        self,
        user_id: Optional[str] = None,
        arguments: Optional[dict] = None,
        provider_id: Optional[str] = None,
        provider: Optional[dict] = None,
        static_dir: Optional[Path] = None,
    ):

        self.user_id = user_id
        self.arguments = arguments or dict()
        self.static_dir = static_dir
        self.provider = get_provider(user_id=user_id, provider_id=provider_id, provider=provider)
        self.hooks = dict()

        self.setup_handlers()

    def setup_handlers(self):
        # обработчики датасетов различных типов
        self.handlers = {'json': self.from_json, 'sql': self.from_sql, 'visiology': self.from_visiology}

    def get_provider(self, raw, adapter=False):
        provider = self.provider

        if raw.get('provider'):
            provider = get_provider(user_id=self.user_id, provider=raw['provider'])

        if provider is None and raw and adapter:
            provider = SQLITE_DIALECT

        return provider

    def get_adapter_provider(self, raw, adapter_provider=None):
        provider = None

        if 'adapter' in raw:
            provider = adapter_provider or self.get_provider(raw['adapter'], adapter=True)

        return provider

    def get_hook(self, conn, **kwargs):
        if conn:
            if conn == SQLITE_DIALECT:
                hook_id = SQLITE_DIALECT
                hook_cls = SqlHook
            else:
                hook_id = conn.id
                hook_cls = ViHook if conn.type == ProviderType.VIQUBE else SqlHook  # @UndefinedVariable

            if hook_id not in self.hooks:
                self.hooks[hook_id] = hook_cls(conn, **kwargs)

            hook = self.hooks[hook_id]
        else:
            hook = None

        return hook

    def get_query(self, raw):
        query = None

        if 'query' in raw:
            query_type = raw.get('type')
            if query_type == 'visiology':
                query = raw['query']
            elif query_type == 'sql':
                querier = get_querier(provider=self.provider, raw=raw)
                query = querier.get_sql_select(querier.raw)

        return query

    def adapt(self, name, data=None, columns=None, adapter_provider=None):
        """Добавляет данные в схему для адаптации как таблицу под переданным именем."""
        if data and adapter_provider:
            columns = columns or list()
            hook = self.get_hook(adapter_provider)
            querier = get_querier(hook=hook)
            querier.create_table(name, columns, temporary=True)
            querier.insert_many(name, columns, data)

    def adapted(self, raw, data, adapter_provider=None):
        """Возвращает даннные, предварительно их адаптируя, если требуется."""
        adapted = data

        if 'adapter' in raw:
            adapter_provider = self.get_adapter_provider(raw, adapter_provider)
            raw['adapter']['type'] = 'sql'
            adapted = self.from_sql(raw['adapter'], adapter_provider)

        return adapted

    def from_json(self, raw, provider, default=None):
        """Возвращает JSON датасет из сырого JSON описания."""
        default = default or dict
        adapter_provider = self.get_adapter_provider(raw)
        data = raw.get('data', raw.get('query', default()))
        columns = raw.get('columns', list())

        if adapter_provider:
            # постобработка возможна только для датасетов в виде списка списков
            self.adapt(raw['name'], data=data, columns=columns, adapter_provider=adapter_provider)
            data = self.adapted(raw, data, adapter_provider=adapter_provider)

        return data

    def from_sql(self, raw, provider, default=None):
        """Возвращает JSON датасет из сырого postgresql запроса, представленного в JSON формате."""
        adapter_provider = self.get_adapter_provider(raw)
        query = self.get_query(raw)
        hook = self.get_hook(provider)
        columns = raw.get('columns', list())
        data = hook.execute(query, select=True, form=raw['form']) if hook else list()
        self.adapt(raw.get('name', 'adapter'), data=data, columns=columns, adapter_provider=adapter_provider)
        data = self.adapted(raw, data, adapter_provider=adapter_provider)

        return data

    def from_visiology(self, raw, provider, default=None):
        """Возвращает JSON датасет из сырого viqube запроса."""
        adapter_provider = self.get_adapter_provider(raw)
        adapter_hook = self.get_hook(adapter_provider)
        unit = get_unit(raw['endpoint'])
        hook = self.get_hook(provider, unit=unit)
        query = self.get_query(raw)
        data = get_from_visiology(hook, raw['endpoint'], raw['name'], query, adapter_hook=adapter_hook)

        return self.adapted(raw, data, adapter_provider=adapter_provider)

    def from_any(self, raw):
        defaults = {'dict': dict, 'list': list}

        if 'type' not in raw:
            raw['type'] = 'json'

        handler = raw['type']
        provider = self.get_provider(raw)
        raw_default = raw.get('default')

        default = defaults.get(raw_default)

        return self.handlers[handler](raw, provider, default=default)

    def get_data(self, dataset):
        """Возвращает развернутый из разных источников набор данных в формате JSON.
        На входе ожидает список наборов данных (dataset).
        """
        data = dict()

        for item in dataset:
            data[item['name']] = self.from_any(item)

        for hook in self.hooks:
            self.hooks[hook].disconnect()

        return data


def get_producer(
    user_id: Optional[str] = None,
    arguments: Optional[dict] = None,
    provider_id: Optional[str] = None,
    provider: Optional[dict] = None,
    static_dir: Optional[Path] = None,
    producer_cls: Optional[Type[Producer]] = None,
):
    """Возвращает провайдер данных из различных источников."""
    if arguments is None:
        arguments = dict()

    producer_cls = producer_cls or Producer
    producer = producer_cls(
        user_id=user_id, arguments=arguments, provider_id=provider_id, provider=provider, static_dir=static_dir
    )

    return producer


def populate_fields(
    groups: Union[list, dict],
    user_id: Optional[str] = None,
    provider_id: Optional[str] = None,
    provider: Optional[dict] = None,
):
    """Возвращает report.parameters, datagrid.filters, datagrid.columns с датасетами опций select."""
    fields = list()
    groups = groups or dict()
    groups = groups if isinstance(groups, list) else groups.get('groups', list())

    if provider:
        producer = get_producer(user_id=user_id, provider_id=provider_id, provider=provider)
    else:
        producer = None

    for raw_group in groups:
        group = {'label': raw_group.get('label', ''), 'fields': list()}

        group_provider = raw_group.get('provider')
        if group_provider:
            group_producer = get_producer(user_id=user_id, provider=group_provider)
        else:
            group_producer = None

        for parameter in raw_group.get('fields', list()):
            if raw_options := parameter.get('options'):
                if isinstance(raw_options, dict):
                    raw_options['name'] = parameter['name']
                    options_type = raw_options['type']

                    if options_type in ('sql',):
                        if 'form' not in raw_options:
                            raw_options['form'] = 'list'

                        param_provider = raw_options.get('provider')
                        if param_provider:
                            param_producer = get_producer(user_id=user_id, provider=param_provider)
                        else:
                            param_producer = None

                        current_producer = param_producer or group_producer or producer

                        if not current_producer:
                            raise DataException(f"Не определен источник данных параметра {parameter['name']}")

                        data = current_producer.from_any(raw_options)
                    elif options_type == 'json':
                        data = raw_options['query']
                    else:
                        raise DataException(f'Тип опций {options_type} не поддерживается')

                    options = list()
                    for row in data:
                        if row:
                            value = row[0]
                            label = row[1] if len(row) > 1 else value

                            options.append({'value': value, 'label': label})

                    parameter['options'] = options
                else:
                    parameter['options'] = raw_options

            group['fields'].append(parameter)

        fields.append(group)

    return fields

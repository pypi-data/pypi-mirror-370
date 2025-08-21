""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import re
import asyncio

from time import time
from copy import deepcopy
from urllib.parse import urljoin
from aiohttp import ClientSession, TCPConnector
from polyants.polyhub.helpers.sqlapi import get_querier
from polyants.polyhub.exceptions import ViAsyncException
from polyants.internal import log

re_queries = {'rawquery': re.compile(r'\/?viqube\/metadata\/rawdata\/query', flags=re.RegexFlag.IGNORECASE)}


async def save_data(adapter_hook, table, data):
    if data.get('values'):
        # записываем данные
        columns = list()
        records = list()
        querier = get_querier(hook=adapter_hook)

        for column in data['columns']:
            columns.append({'name': column['header'], 'type': column['datatype']})

        for row in data['values']:
            records.append([querier.pythonize(v, columns[i]['type']) for i, v in enumerate(row)])

        querier.insert_many(table, columns, records)
    else:
        raise ViAsyncException(f'Данные для {table} не получены')


async def get_data(session, url, headers, query, data, adapter_hook=None, table=None):
    try:
        r = await session.request(method='POST', url=url, headers=headers, json=query)
    except Exception as e:
        headers['Authorization'] = '*******'
        raise ViAsyncException(f'{url}, хидеры:\n{headers}\nошибка {e.__class__.__name__}:\n{e}')

    # `in` т.к. может быть указан charset, а еще, возможно, стоит учитывать `x-json`
    if 'application/json' in r.headers.get('content-type', ''):
        answer = await r.json()
    else:
        answer = await r.text()

    if r.status != 200:
        query = f'\nтело:\n{query}' if query is not None else ''
        msg = f'{url}, код ошибки: {r.status}, ответ:\n{answer}{query}'
        raise ViAsyncException(msg)

    if adapter_hook and table:
        # инициируем сохранение полученных данных для SQL обработки
        await save_data(adapter_hook, table, answer)
    else:
        if 'columns' in answer and 'values' in answer:
            if not data['columns']:
                data['columns'] = answer['columns']

            data['values'].extend(answer['values'])


async def get_and_save(vihook, endpoint, queries, data, adapter_hook=None, table=None):
    """Асинхронно получает данные из викуба, не превышая пулл соединений.
    При необходимости подготавливает их для SQL обработки.
    """
    connector = TCPConnector(limit_per_host=vihook.pool)
    url = urljoin(vihook.conn['entry_point'], endpoint)

    headers = {'X-API-VERSION': vihook.api_version, 'Authorization': vihook.auth_string}

    async with ClientSession(connector=connector) as session:
        tasks = []
        for query in queries:
            tasks.append(get_data(session, url, headers, query, data, adapter_hook=adapter_hook, table=table))
        await asyncio.gather(*tasks)


def get_endpoint_type(endpoint):
    for k, v in re_queries.items():
        if v.match(endpoint):
            type_ = k
            break
    else:
        raise ViAsyncException(f'Неизвестный тип запроса Visiology: {endpoint}')

    return type_


def get_from_visiology(vihook, endpoint, table, query, adapter_hook=None):
    """Асинхронное получение данных из викуба."""
    log.debug('Запрос к викубу:\n%s', query)

    get_endpoint_type(endpoint)

    query_limit = query.get('limit', 0)
    if query_limit < 0:
        ViAsyncException(f'Отрицательный limit {query_limit} в запросе')

    query_offset = query.get('offset', 0)
    if query_offset < 0:
        ViAsyncException(f'Отрицательный offset {query_offset} в запросе')

    # получаем данные пачками, максимальное количество которых, ограничено лимитом получаемых записей
    limit_batches = -(-query_limit // vihook.batch)

    # узнаем количество записей таблицы
    count_query = {'database': query['database'], 'mgid': query['mgid']}

    if 'filter' in query and query['filter']:
        count_query['filter'] = query['filter']

    records_count = vihook.call('viqube/metadata/rawdata/getcount', data=count_query)
    records_count = records_count.get('count', 0)
    # сначала применяется фильтр, затем оффсет
    records_count = records_count - query_offset
    if records_count < 0:
        records_count = 0

    # если количество записей таблицы ниже лимита, то количество пачек считаем от них
    count_batches = -(-records_count // vihook.batch)
    batches = min(limit_batches, count_batches) if limit_batches else count_batches

    if adapter_hook:
        # определяем структуру таблицы
        current_query = deepcopy(query)
        current_query['offset'] = 0
        current_query['limit'] = 1

        answer = vihook.call(endpoint, data=current_query)

        if answer.get('columns'):
            # создаем таблицу, если ее еще нет
            columns = list()
            for __, column in enumerate(answer['columns']):
                columns.append({'name': column['header'], 'type': column['datatype']})

            querier = get_querier(hook=adapter_hook)
            querier.create_table(table, columns, temporary=True)
        else:
            raise ViAsyncException(f'Структура таблицы {table} не определена')

    # генерируем запросы для каждой пачки
    queries = list()

    step = min(vihook.batch, query_limit) if query_limit else vihook.batch

    # выполняем хотя бы один запрос, т.к. не все типы запросов поддерживают пачки
    if not batches:
        batches = 1
        log.warning(f'Получаем данные в один поток для {endpoint}')

    for batch in range(batches):
        current_query = deepcopy(query)
        current_query['offset'] = query.get('offset', 0) + batch * step
        current_query['limit'] = step
        queries.append(current_query)

    # fetched raw data container
    data = {'columns': list(), 'values': list()}

    # получаем записи асинхронно
    start = time()
    asyncio.run(get_and_save(vihook, endpoint, queries, data, adapter_hook=adapter_hook, table=table))
    log.debug(f'Асинхронный запрос выполнен за {time() - start}с')

    return data

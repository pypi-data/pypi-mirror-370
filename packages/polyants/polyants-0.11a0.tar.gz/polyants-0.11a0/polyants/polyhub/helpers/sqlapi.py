""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import pyodbc
import sqlite3
import psycopg2
import sqlparse

from typing import Union
from time import time
from abc import ABCMeta
from copy import copy, deepcopy
from dataclasses import dataclass
from psycopg2.extras import execute_values
from psycopg2.errors import DataError, ProgrammingError
from jsqlib import Query
from polyants.polyhub.enums import ProviderType
from polyants.internal import log
from polyants.polyhub.constants import SQLITE_DIALECT
from polyants.polyhub.exceptions import SqlApiException, ProviderException, SqlApiDataException, SqlApiQueryException

END_ROLE = 'end'
BEGIN_ROLE = 'begin'


class Hook:
    def __init__(self, provider, **kwargs):
        self.provider = provider
        self.dialect = self._get_dialect()
        self.conn = self._get_conn()
        self.connected = False

    def _get_dialect(self):
        if self.provider == SQLITE_DIALECT:
            dialect = SQLITE_DIALECT
        else:
            dialect = self.provider.type.value

        if dialect not in (ProviderType.MSSQL.value, ProviderType.POSTGRESQL.value, SQLITE_DIALECT):
            raise SqlApiException(f'Неизвестный тип подключения: {dialect}')

        return dialect

    def _get_conn_string(self):
        if self.dialect == SQLITE_DIALECT:
            result = ''
        else:
            if self.dialect == ProviderType.MSSQL.value:
                port = self.provider.port or '1433'
                string = 'DRIVER=ODBC Driver 17 for SQL Server;SERVER={};PORT={};DATABASE={};UID={};PWD={}'
            elif self.dialect == ProviderType.POSTGRESQL.value:
                port = self.provider.port or '5432'
                string = "host='{}' port='{}' dbname='{}' user='{}' password='{}'"

            result = string.format(
                self.provider.host, port, self.provider.db, self.provider.login, self.provider.password
            )

        return result

    def _get_conn(self):
        if self.dialect == SQLITE_DIALECT:
            log.debug(f'Соединение с in-memory {self.dialect}...')
            conn = sqlite3.connect('')
        else:
            conn_string = self._get_conn_string()

            log.debug(f'Соединение {self.dialect} с {self.provider.host}...')

            if self.dialect == ProviderType.MSSQL.value:
                conn = pyodbc.connect(conn_string, autocommit=False)
                conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
                conn.setencoding(encoding='utf-8')
            elif self.dialect == ProviderType.POSTGRESQL.value:
                conn = psycopg2.connect(conn_string)

        self.connected = True
        log.debug('...установлено')

        return conn

    def execute(self, sql, select=False, form=None):
        r = None

        if sql:
            statements = sqlparse.split(sql)
            try:
                sql = statements[0]
            except IndexError:
                raise SqlApiException(f'Не найден SQL запрос в:\n{sql}')

            c = None
            start = time()

            try:
                c = self.conn.cursor()
                c.execute(sql)

                if select:
                    if form == 'one':
                        try:
                            r = [dict((c.description[i][0], value) for i, value in enumerate(c.fetchone()))][0]
                        except IndexError as e:
                            raise SqlApiException(f'Форма one требует select не менее одной строки, ошибка: {e}')
                    elif form == 'dict':
                        try:
                            r = dict(c.fetchall())
                        except ValueError as e:
                            raise SqlApiException(f'Форма dict требует select ровно двух полей, ошибка: {e}')
                    else:
                        r = c.fetchall()

            except Exception as e:
                if not select:
                    self.conn.rollback()

                msg = f'Ошибка SQL {e.__class__.__name__}: {e}'
                log.error(f'{msg}\nзапрос: {sql}')
                self.conn.close()

                if isinstance(e, DataError):
                    raise SqlApiDataException(msg)
                elif isinstance(e, ProgrammingError):
                    raise SqlApiQueryException(msg)
                else:
                    raise SqlApiException(msg)

            finally:
                if hasattr(self.conn, 'closed') and not self.conn.closed:
                    if not select:
                        self.conn.commit()

                    if c:
                        c.close()

                log.debug(f'Запрос выполнен за {time() - start}с')

            log.debug('Запрос:\n%s\nрезультат:\n%s', sql, r)
        else:
            log.debug('На выполнение был отправлен пустой запрос')

        return r

    def disconnect(self):
        if self.connected:
            self.conn.close()
            self.connected = False


def squote(value):
    return f'''<-{value.replace("'", "''")}->''' if isinstance(value, str) else value


def dquote(value):
    return f'<={value}=>'


@dataclass
class Column:
    idx: int
    name: str
    type: str
    primary: bool = False
    readonly: bool = False
    foreign: bool = False
    calculated: bool = False
    ignore: str = ''
    role: str = ''

    def __eq__(self, other):
        return self.idx == self.other if isinstance(other, type(self)) else self.idx == other

    def __repr__(self):
        return (
            f'{self.idx=}, {self.name=}, {self.type=}, {self.primary=}, {self.readonly=}'
            f', {self.foreign=}, {self.calculated=}, {self.ignore=}, {self.role=}'
        )

    @property
    def quoted(self):
        return dquote(self.name)


class Scope(list):
    def __getitem__(self, column):
        for c in self:
            if c.idx == column:
                return c


class Querier(metaclass=ABCMeta):
    def __init__(self, hook=None, provider=None, raw=None, sort=None, filter_=None, limit=None, offset=None):
        self.raw = raw or dict()
        log.debug('self.raw query: %s', self.raw)
        self.provider = provider
        self.sort = sort or list()
        self.filter = filter_.get('body', dict()) if filter_ else None
        log.debug('self.filter: %s', self.filter)
        self.limit = limit
        self.offset = offset
        self._hook = hook
        self._table = None
        self._columns = None
        self._filters = None
        self._lookups = None
        self._flat_columns = None
        self._column_objects = None
        self._tangibles = None
        self._primaries = None
        self._writables = None
        self._select_columns = None
        self._table_select = None
        self._raw_select = None

    @property
    def hook(self):
        if self._hook is None:
            self._hook = Hook(self.provider)

        return self._hook

    @property
    def table(self):
        if self._table is None:
            self._table = self.raw.get('entity', '')

        return self._table

    @property
    def columns(self):
        """Возвращает описание колонок основного селекта."""
        if self._columns is None:
            self._columns = self.raw.get('columns', list())

        return self._columns

    @property
    def column_objects(self):
        if self._column_objects is None:
            self._column_objects = list()

            for group in self.columns:
                for idx, c in enumerate(group.get('fields', list())):
                    self._column_objects.append(
                        Column(
                            idx=idx,
                            name=c['name'],
                            type=self.get_column_type(c),
                            primary=c.get('primary', False),
                            readonly=c.get('readonly', False),
                            foreign=c.get('foreign', False),
                            calculated=self.is_column_calculated(c),
                            ignore=str(c.get('ignore', '')),
                            role=c.get('role', ''),
                        )
                    )
            log.debug('_column_objects: %s', self._column_objects)

        return self._column_objects

    @property
    def tangibles(self):
        if self._tangibles is None:
            self._tangibles = [c for c in self.column_objects if not c.calculated]
            log.debug('_tangibles: %s', self._tangibles)

        return self._tangibles

    @property
    def primaries(self):
        if self._primaries is None:
            self._primaries = [c for c in self.tangibles if c.primary]
            log.debug('_primaries: %s', self._primaries)

        return self._primaries

    @property
    def writables(self):
        if self._writables is None:
            self._writables = [c for c in self.tangibles if not c.readonly and not c.foreign]
            log.debug('_writables: %s', self._writables)

        return self._writables

    @property
    def select_columns(self):
        if self._select_columns is None:
            self._select_columns = [{'eval': c.quoted} for c in self.tangibles]
            log.debug('_select_columns: %s', self._select_columns)

        return self._select_columns

    @property
    def filters(self):
        """Возвращает допустимые фильтры датасета."""
        if self._filters is None:
            self._filters = self.raw.get('setup', dict()).get('filters', list())
            log.debug('_filters: %s', self._filters)

        return self._filters

    @property
    def lookups(self):
        """Возвращает описание лукапов датасета."""
        if self._lookups is None:
            self._lookups = self.raw.get('setup', dict()).get('lookups', list())
            log.debug('_lookups: %s', self._lookups)

        return self._lookups

    @property
    def types(self):
        """Словарь соответствия типов диалекта и типов в интерфейсе."""
        return {
            'long': 'integer',
            'short': 'integer',
            'datetime': 'timestamp',
            'string': 'varchar',
            'number': 'numeric',
            'checkbox': 'boolean',
            'datetime-local': 'timestamp',
        }

    @property
    def table_select(self):
        if self._table_select is None:
            self._table_select = {"query": {"select": self.select_columns, "from": [{"name": self.table}]}}
            log.debug('_table_select: %s', self._table_select)

        return self._table_select

    @property
    def raw_select(self):
        """Строит запрос и добавляет в него пользовательские сортировку и фильтрацию."""
        if self._raw_select is None:
            log.debug('raw_select')
            where = self.where_filter(self.filter)

            sort = list()
            for i in self.sort:
                item = {"value": dquote(i['column'])}

                if i.get('desc', False):
                    item['desc'] = True

                sort.append(item)

            if select := self.raw.get('select'):
                if where or sort:
                    subquery = {"alias": "t", "enclose": select.get('query', dict())}
                    raw = {"query": {"select": self.select_columns, "from": [subquery]}}
                else:
                    raw = select
            elif self.table:
                raw = self.table_select
            else:
                raise ProviderException('Select не определен')

            if where:
                log.debug('    where: %s', where)
                raw['query']['where'] = where
            if sort:
                log.debug('    sort: %s', sort)
                raw['query']['order by'] = sort

            if self.limit:
                raw['query']['limit'] = self.limit
            if self.offset:
                raw['query']['offset'] = self.offset

            log.debug('    raw: %s', raw)
            self._raw_select = raw

        return self._raw_select

    @classmethod
    def pythonize(cls, value, type_):
        """Возвращает python совместимое значение."""
        return value

    @classmethod
    def guess_type(cls, value):
        types = {
            'int': 'integer',
            'float': 'real',
            'bool': 'boolean',
            'str': 'varchar',
            'NoneType': 'varchar',
            'Decimal': 'real',
        }

        return types.get(type(value).__name__, value)

    @classmethod
    def is_column_looked_up(cls, column):
        return bool(column.get('parent') and column.get('lookup'))

    @classmethod
    def is_column_calculated(cls, column):
        if 'calculated' in column:
            return column['calculated']

        return cls.is_column_looked_up(column) and not column.get('foreign')

    def _get_column_lookup(self, column: dict) -> dict | None:
        for lookup in self.lookups:
            if (l := column.get('lookup')) and l['id'] == lookup:  # noqa: E741
                key = l.get('key', l.get('label'))
                for columns in self.lookups[lookup].get('columns', list()):
                    for f in columns['fields']:
                        if key == f['name']:
                            return f

        return None

    def _get_column_by_name(self, name, strict=True):
        for column in self.column_objects:
            if column.name == name:
                return column
        else:
            if strict:
                raise SqlApiException(f'Атрибут `{name}` не найден')

    def _get_column_by_role(self, role, strict=True):
        for column in self.column_objects:
            if column.role == role:
                return column
        else:
            if strict:
                raise SqlApiException(f'Атрибут с ролью `{role}` не найден')

    def _cleanse_data(self, data, columns=None):
        """Убирает неизвестные атрибуты и их значения.
        Также убирает атрибуты, полученные значения которых следует игнорировать.
        """
        log.debug('_cleanse_data')
        len_columns = len(data[0])
        cleansed = list()
        known = list()
        known_columns = list()

        if columns:
            log.debug('    columns: %s', columns)
            len_columns = len(columns)

            if len_columns != len(set(columns)):
                raise SqlApiException('Обнаружено дублирование переданных атрибутов')

            column_names = [i.name for i in self.column_objects]
            for idx, column in enumerate(columns):
                if column in column_names:
                    # атрибут задан в документе
                    known.append(idx)
                    known_columns.append(column)
                else:
                    log.info(f'Атрибут {column} не определен в документе')

            if not known_columns:
                raise SqlApiException('Не переданы известные атрибуты')

        for idx, row in enumerate(data):
            if len(row) != len_columns:
                raise SqlApiException(f'Количество значений в строке {idx} не равно {len_columns}')

            cleansed.append([v for i, v in enumerate(row) if not known or i in known])

        return (known_columns, cleansed)

    def _filter_column_objects(self, column_objects=None, checklist=None):
        """Возвращает набор атрибутов, составленный из переданного,
        оставляя только присутствующие в контрольном списке,
        и сортируя их соответственно.
        """
        log.debug('_filter_column_objects: %s by %s', column_objects, checklist)
        result = column_objects

        if checklist:
            filtered = [None] * len(checklist)

            for co in column_objects:
                for idx, c in enumerate(checklist):
                    if co.name == c:
                        found = copy(co)
                        found.idx = idx
                        filtered[idx] = found
                        break

            result = list(filter(None, filtered))
            log.debug('    filtered: %s', result)

        return result

    def _adapt(self, condition):
        log.debug('adapt: %s', condition)
        adapted = dict()

        operation = condition.get('operation')
        column = self.get_filter_column(condition.get('name'))
        value = condition.get('value')

        if operation and column:
            log.debug('    adapting operation %s on column %s', operation, column)

            if value:
                log.debug('    condition value: %s', value)

                if operation in ('contains', 'not contains'):
                    operation = operation.replace('contains', 'like')
                elif operation in ('in', 'not in'):
                    args = [dquote(column)]
                    value = [squote(v) for v in value]
                    args.extend(value)
                    adapted = {operation: args}
                elif operation in ('valid'):
                    dt_begin = self._get_column_by_name(column)
                    if dt_begin.role != BEGIN_ROLE:
                        raise SqlApiException(f'Роль атрибута `{column}` должна быть `begin`')

                    dt_end = self._get_column_by_role(END_ROLE)

                    adapted = {
                        'and': [
                            {'lte': [dquote(dt_begin.name), squote(value)]},
                            {'gt': [dquote(dt_end.name), squote(value)]},
                        ]
                    }
            if not adapted:
                log.debug('    direct adaptation of value `%s`', value)
                if value is None or value is True or value is False:
                    if operation == 'eq':
                        operation = 'is'
                    elif operation == 'neq':
                        operation = 'is not'
                adapted = {operation: [dquote(column), squote(value)]}
        else:
            log.debug('    inplace condition: `%s`', condition)
            adapted = condition

        return adapted

    def _get_equality_condition(self, left_alias, right_alias, extra=None):
        """Возвращает конструкцию сравнения по ключевым полям датасета.
        extra - дополнительные условия сравнения.
        """
        condition = list()
        for column in self.primaries:
            condition.append({"eq": [f"<={left_alias}.{column.name}=>", f"<={right_alias}.{column.name}=>"]})
        for c in extra:
            condition.append(c)

        return {"and": condition}

    def _get_historical_select(self, columns):
        log.debug('_get_historical_select: %s', columns)
        select = list()
        for column in columns:
            if column.role in (BEGIN_ROLE, END_ROLE):
                select.append({"eval": {"cast": [column.quoted, "date"]}})
            else:
                select.append({"eval": column.quoted})

        return select

    def get_column_type(self, column):
        type_ = column.get('dataType', column.get('type', 'varchar'))
        if type_ == 'lookup' and not column.get('parent'):
            # ключевой атрибут лукапа
            if lookup := self._get_column_lookup(column):
                type_ = lookup.get('dataType', lookup.get('type', 'varchar'))
            else:
                SqlApiException(f'Не найден лукап атрибута `{column["name"]}`')

        return self.types.get(type_, type_)

    def get_filter_column(self, name):
        found = False
        column = None

        if name:
            for group in self.filters:
                if found:
                    break

                for i in group.get('fields', list()):
                    if i['name'] == name:
                        found = True
                        column = i.get('column', name)
                        break

        return column

    def where_filter(self, filter_):
        log.debug('where_filter: %s', filter_)
        if isinstance(filter_, dict):
            if 'operation' in filter_:
                return self._adapt(filter_)
            else:
                if 'and' in filter_:
                    filter_['and'] = self.where_filter(filter_['and'])
                if 'or' in filter_:
                    filter_['or'] = self.where_filter(filter_['or'])

        elif isinstance(filter_, list):
            for idx, i in enumerate(filter_):
                if 'operation' in filter_:
                    filter_[idx] = self._adapt(i)
                else:
                    filter_[idx] = self.where_filter(i)

        return filter_

    def get_sql_select(self, raw):
        log.debug('get_sql_select')
        query = Query(deepcopy(raw))

        return query.sql

    def execute(self, sql, select=False, form=None):
        """Выполняет запрос."""
        return self.hook.execute(sql, select=select, form=form)

    def select(self):
        """Выполняет запрос, с учетом переданных фильтров и сортировки, и возвращает результат."""
        log.debug('select')
        sql = self.get_sql_select(self.raw_select)

        return self.execute(sql, select=True) if sql else list()

    def count(self):
        log.debug('count')
        if not (raw := self.raw.get('count')):
            log.debug('    auto')
            select = deepcopy(self.raw_select.get('query', dict()))
            select.pop('limit', None)
            select.pop('offset', None)
            subquery = {"alias": "t", "enclose": select}

            raw = {"query": {"select": [{"eval": {"count": ["*"]}}], "from": [subquery]}}

        sql = self.get_sql_select(raw)

        try:
            cnt = self.execute(sql, select=True, form='list')[0][0] if sql else 0
        except IndexError:
            cnt = 0

        return cnt

    def set_values(self, raw: Union[dict, list], data: list) -> dict:
        """Находит все ключи `values` с пустым `[]` и заменяет каждый из них на `data`."""
        if isinstance(raw, dict):
            for k in raw:
                if 'values' in raw:
                    if not raw['values']:
                        raw['values'] = data
                else:
                    self.set_values(raw[k], data)

        elif isinstance(raw, list):
            for idx, i in enumerate(raw):
                raw[idx] = self.set_values(i, data)

        return raw

    def default_or_squote(self, value, column):
        return 'default' if column.ignore and str(value) == column.ignore else squote(value)

    def quoted_values(self, values, scope=None, use_defaults=False):
        data = list()
        scope = Scope(scope or self.column_objects)

        if use_defaults:
            for row in values:
                data.append([self.default_or_squote(i, scope[idx]) for idx, i in enumerate(row) if idx in scope])
        else:
            for row in values:
                data.append([squote(i) for idx, i in enumerate(row) if idx in scope])

        return data

    def insert(self, data, columns=None):
        """Добавление данных.
        Если `insert` кастомный, он должен содержать пустой набор данных `"values": []`.
        Для вставки используются данные только записываемых атрибутов.
        """
        log.debug('insert')
        if data:
            columns, cleansed = self._cleanse_data(data, columns=columns)
            writables = self._filter_column_objects(column_objects=self.writables, checklist=columns)

            if insert := self.raw.get('insert'):
                log.debug('    custom')
                raw = self.set_values(insert, self.quoted_values(cleansed, scope=writables))
            else:
                log.debug('    auto')
                values = self.quoted_values(cleansed, scope=writables)

                if (begin_column := self._get_column_by_role(BEGIN_ROLE, strict=False)) and (
                    end_column := self._get_column_by_role(END_ROLE, strict=False)
                ):
                    # вставка историчных данных
                    log.debug('    historical')
                    raw = {
                        "with": {
                            "dataset": {
                                "columns": [c.name for c in writables],
                                "select": [{"eval": "t.*"}],
                                "from": [{"name": "t", "values": values}],
                            },
                            "upsert": {
                                "update": {
                                    "name": self.table,
                                    "alias": "b",
                                    "set": [
                                        {
                                            "name": end_column.name,
                                            "eval": {"cast": [f"<=d.{begin_column.name}=>", "date"]},
                                        }
                                    ],
                                },
                                "from": [{"name": "dataset", "alias": "d"}],
                                "where": self._get_equality_condition(
                                    'b',
                                    'd',
                                    extra=[
                                        {
                                            "eq": [
                                                f"<=b.{end_column.name}=>",
                                                {"cast": [f"<=d.{end_column.name}=>", "date"]},
                                            ]
                                        }
                                    ],
                                ),
                                "returning": ["<=b=>.*"],
                            },
                        },
                        "insert": {
                            "name": self.table,
                            "columns": [c.name for c in writables],
                            "select": self._get_historical_select(writables),
                            "from": [{"name": "dataset"}],
                        },
                    }
                else:
                    log.debug('    default')
                    raw = {
                        "query": {
                            "insert": {
                                "name": self.table,
                                "columns": [c.name for c in writables],
                                "values": self.quoted_values(cleansed, scope=writables, use_defaults=True),
                            }
                        }
                    }

            return self.execute(self.get_sql_select(raw))

    def update(self, data, columns=None):
        """Изменение данных.
        Если `update` кастомный, он должен содержать пустой набор данных `"values": []`.
        """
        log.debug('update')
        if data:
            columns, cleansed = self._cleanse_data(data, columns=columns)
            tangibles = self._filter_column_objects(column_objects=self.tangibles, checklist=columns)
            values = self.quoted_values(cleansed, scope=tangibles)

            if update := self.raw.get('update'):
                log.debug('    custom')
                raw = self.set_values(update, values)
            else:
                log.debug('    auto')
                set_ = list()
                writables = self._filter_column_objects(column_objects=self.writables, checklist=columns)
                primaries = self._filter_column_objects(column_objects=self.primaries, checklist=columns)

                if not writables:
                    raise SqlApiException('Не переданы атрибуты для изменения значений')

                if not primaries:
                    raise SqlApiException('Не переданы ключевые атрибуты')

                for i in writables:
                    cast = {'cast': [dquote(f't.{i.name}'), i.type]}
                    set_.append({'name': i.name, 'eval': cast})

                where = list()
                for i in primaries:
                    cast = {'cast': [dquote(f't.{i.name}'), i.type]}
                    where.append({'eq': [dquote(f'{self.table}.{i.name}'), cast]})

                raw = {
                    "query": {
                        "update": {"name": self.table, "set": set_},
                        "from": [{"name": "t", "values": values, "columns": [c.name for c in tangibles]}],
                    }
                }

                if where:
                    raw['query']['where'] = {'and': where}

            return self.execute(self.get_sql_select(raw))

    def delete(self, data, columns=None):
        """Удаление данных.
        Если `delete` кастомный, он должен содержать пустой набор данных `"values": []`.
        """
        log.debug('delete')
        if data:
            columns, cleansed = self._cleanse_data(data, columns=columns)
            tangibles = self._filter_column_objects(column_objects=self.tangibles, checklist=columns)
            values = self.quoted_values(cleansed, scope=tangibles)

            if delete := self.raw.get('delete'):
                log.debug('    custom')
                raw = self.set_values(delete, values)
            else:
                log.debug('    auto')
                where = list()
                primaries = self._filter_column_objects(column_objects=self.primaries, checklist=columns)

                if not primaries:
                    raise SqlApiException('Не переданы ключевые атрибуты')

                for i in primaries:
                    cast = {'cast': [dquote(f't.{i.name}'), i.type]}
                    where.append({'eq': [dquote(f'{self.table}.{i.name}'), cast]})

                if (begin_column := self._get_column_by_role(BEGIN_ROLE, strict=False)) and (
                    end_column := self._get_column_by_role(END_ROLE, strict=False)
                ):
                    # удаление историчных данных
                    log.debug('    historical')
                    raw = {
                        "with": {
                            "dataset": {
                                "columns": [с.name for с in tangibles],
                                "select": [{"eval": "t.*"}],
                                "from": [{"name": "t", "values": values}],
                            },
                            "upsert": {
                                "update": {
                                    "name": self.table,
                                    "alias": "b",
                                    "set": [
                                        {
                                            "name": end_column.name,
                                            "eval": {"cast": [f"<=d.{end_column.name}=>", "date"]},
                                        }
                                    ],
                                },
                                "from": [{"name": "dataset", "alias": "d"}],
                                "where": self._get_equality_condition(
                                    'b',
                                    'd',
                                    extra=[
                                        {
                                            "eq": [
                                                f"<=b.{end_column.name}=>",
                                                {"cast": [f"<=d.{begin_column.name}=>", "date"]},
                                            ]
                                        }
                                    ],
                                ),
                                "returning": ["<=b=>.*"],
                            },
                        },
                        "delete": {"name": self.table},
                        "where": {
                            "in": [
                                {"enclose": [с.quoted for с in tangibles]},
                                {"select": self._get_historical_select(tangibles), "from": [{"name": "dataset"}]},
                            ]
                        },
                    }
                else:
                    log.debug('    default')
                    raw = {
                        "query": {
                            "delete": {
                                "name": self.table,
                                "using": [{"name": "t", "values": values, "columns": [c.name for c in tangibles]}],
                            },
                            "where": {'and': where},
                        }
                    }

            return self.execute(self.get_sql_select(raw))

    def create_table(self, name, columns, temporary=False):
        """Создает таблицу name с переданными в columns атрибутами.
        Формат columns: [{'name': 'column_name', 'type': 'column_type'}]
        """
        log.debug('create_table')
        if name and columns:
            log.debug('    name: %s', name)
            attrs = list()
            sql = 'create'

            if temporary:
                sql += ' temporary'

            sql += f' table "{name}" ('

            for column in columns:
                attrs.append(f"{column['name']} {self.get_column_type(column)}")

            sql += ','.join(attrs)
            sql += ')'
            log.debug(f'    ddl:\n{sql}')
            self.execute(sql)

    def insert_many(self, table, columns, data):
        """Вставляет в таблицу table переданные данные.
        Формат:
            columns: [{'name': 'column_name', 'type': 'column_type'},]
            data: [[value_n, value_m,],]
        """
        log.debug('insert_many')
        if data:
            log.debug('    data')
            attrs = [i['name'] for i in columns]
            sql = f'insert into "{table}" ({",".join(attrs)}) values %s'
            c = self.hook.conn.cursor()
            execute_values(c, sql, data)
            c.close()
            self.hook.conn.commit()


class QuerierPG(Querier):
    """Генерация и исполнение запроса в Postgres."""


class QuerierLite(Querier):
    """Генерация и исполнение запроса в SQLite."""

    @property
    def types(self):
        """Словарь соответствия типов диалекта."""
        return {
            'integer': 'integer',
            'long': 'integer',
            'short': 'integer',
            'boolean': 'integer',
            'real': 'real',
            'datetime': 'datetime',
            'date': 'date',
            'time': 'time',
            'text': 'text',
            'string': 'text',
            'varchar': 'text',
        }

    @classmethod
    def pythonize(self, value, type_):
        """Возвращает python совместимое значение."""
        if type_ == 'boolean' and value is not None:
            value = int(value)

        return value

    def insert_many(self, table, columns, data):
        if data:
            columns_num = len(data[-1])
            substitutions = ','.join(('?' for i in range(columns_num)))
            sql = f'insert into "{table}" values ({substitutions})'
            c = self.hook.conn.cursor()
            c.executemany(sql, data)
            c.close()
            self.hook.conn.commit()


def get_querier(hook=None, provider=None, raw=None, **kwargs):
    """Возвращает экземпляр мастера запросов на основе диалекта."""
    if hook:
        if hook.dialect == SQLITE_DIALECT:
            builder = QuerierLite(hook=hook, raw=raw)
        elif hook.dialect == ProviderType.POSTGRESQL.value:
            builder = QuerierPG(hook=hook, provider=provider, raw=raw, **kwargs)
        else:
            raise ProviderException(f'Провайдер {hook.dialect} не поддерживается')
    elif provider:
        if provider.type == ProviderType.POSTGRESQL:
            builder = QuerierPG(hook=hook, provider=provider, raw=raw, **kwargs)
        else:
            raise ProviderException(f'Провайдер типа {provider.type} не поддерживается')
    elif not provider:
        builder = QuerierLite(provider=SQLITE_DIALECT, raw=raw)
    else:
        raise ProviderException('Не определен провайдер')

    return builder

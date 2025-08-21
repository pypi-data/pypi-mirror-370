""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""


class IOException(Exception):
    pass


class DBException(Exception):
    pass


class OrchestraException(Exception):
    pass


class AdapterException(Exception):
    pass


class ViApiException(Exception):
    pass


class ViAsyncException(Exception):
    pass


class ProviderException(Exception):
    pass


class DataException(Exception):
    pass


class GQLException(Exception):
    pass


class HttpException(Exception):
    pass


class SqlApiException(Exception):
    pass


class SqlApiDataException(SqlApiException):
    pass


class SqlApiQueryException(SqlApiException):
    pass

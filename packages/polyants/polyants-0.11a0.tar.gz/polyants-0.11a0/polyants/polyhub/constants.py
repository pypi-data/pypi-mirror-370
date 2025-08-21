""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import re

from uuid import UUID
from pathlib import PosixPath
from jsonschema import Draft202012Validator

APP_CODE = 'dwash'
DWASH_SCHEMA = APP_CODE

API_SLUG = 'api'
API_PORT = 3000

BACK_CODE = 'back'
REPORT_CODE = 'report'
ALERT_CODE = 'alert'
SKIPPER_CODE = 'skipper'
REDIS_CODE = 'redis'
ORIGIN_CODE = 'origin'
CATALOG_CODE = 'catalog'
CATALOG_PORT = 8585

BACK_HOSTNAME = f'{APP_CODE}-{BACK_CODE}'
ALERT_HOSTNAME = f'{APP_CODE}-{ALERT_CODE}'
REPORT_HOSTNAME = f'{APP_CODE}-{REPORT_CODE}'
SKIPPER_HOSTNAME = f'{APP_CODE}-{SKIPPER_CODE}'
REDIS_HOSTNAME = f'{APP_CODE}-{REDIS_CODE}'
ORIGIN_HOSTNAME = f'{APP_CODE}-{ORIGIN_CODE}'
CATALOG_HOSTNAME = f'{APP_CODE}-{CATALOG_CODE}'

REDIS_HOST = REDIS_HOSTNAME
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

REDIS_PREFIX = f'_{APP_CODE}.'

RCG_CODE = f'{REDIS_PREFIX}group.skipper'
RS_CODE = 'stream-a'
STREAM_INTERRUPT_SIGNAL = 'interrupt-stream'
UPDATE_SUBSCRIPTIONS_ACTION = 'update-subscriptions'
AUTH_SETTINGS_KEY = f'{REDIS_PREFIX}settings:system:auth'

GRPC_PORT = 50051

REPORTS_DB = f'{REPORT_CODE}s'
REPORTS_PATH = f'{REPORT_CODE}ing/{REPORTS_DB}'
CLOUD_PATH = 'cloud'
WINDOWS_PATH = 'windows'
WINDOW_BACKGROUNS = 'backgrounds'
WINDOW_PICTURES = 'pictures'
ALERTS_PATH = 'alerts'
SKIPPER_PATH = 'skipper'
ORCHESTRATORS_PATH = 'orchestrators'
SWAP_PATH = 'swap'

ORIGIN_HOST = f'{ORIGIN_HOSTNAME}:{GRPC_PORT}'
CATALOG_HOST = f'{CATALOG_HOSTNAME}:{CATALOG_PORT}'

REPORTS_SLUG = f'{API_SLUG}/{REPORTS_PATH}'
CLOUD_SLUG = f'{API_SLUG}/{CLOUD_PATH}'
WINDOWS_SLUG = f'{API_SLUG}/{WINDOWS_PATH}'
ORCHESTRATOR_SLUG = f'{API_SLUG}/{ORCHESTRATORS_PATH}'
AUTH_SLUG = f'{API_SLUG}/auth'
LOGIN_SLUG = f'{AUTH_SLUG}/login'
OAUTH2ACF_REDIRECT_SLUG = f'{AUTH_SLUG}/oauth2acf/redirect'
OAUTH2ACF_LOGOUT_SLUG = f'{AUTH_SLUG}/oauth2acf/logout'
CURRENT_AUTH_SLUG = f'{AUTH_SLUG}/current/login'

PUBLIC_SLUG = f'{API_SLUG}/public'

APP_RESOURCES = PosixPath('/www/app/resources')

RESOURCES_ROOT = PosixPath('/www/resources')
REPORTS_ROOT = RESOURCES_ROOT.joinpath(REPORTS_PATH)
CLOUD_ROOT = RESOURCES_ROOT.joinpath(CLOUD_PATH)
WINDOWS_ROOT = RESOURCES_ROOT.joinpath(WINDOWS_PATH)
ALERTS_ROOT = RESOURCES_ROOT.joinpath(ALERTS_PATH)
ORCHESTRATORS_ROOT = RESOURCES_ROOT.joinpath(ORCHESTRATORS_PATH)
SWAP_ROOT = RESOURCES_ROOT.joinpath(SWAP_PATH)

APP_ROOT = PosixPath('/www/app')
TEMPLATES_ROOT = APP_ROOT.joinpath('templates')

GUID_RE = re.compile(r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', flags=re.IGNORECASE)
DICT_HASH = '99914b932bd37a50b983c5e7c90ae93b'
LIST_HASH = 'd751713988987e9331980363e24189ce'

BEARER_TOKEN_HEADER = 'Authorization'
TOKEN_PREFIX = 'Bearer'
INTERNAL_TOKEN_PREFIX = 'Internal'
ACCESS_TOKEN = 'access'
REFRESH_TOKEN = 'refresh'
HS_ALGORITHM = 'HS256'
RS_ALGORITHM = 'RS256'
KNOWN_ALGORITHMS = (HS_ALGORITHM, RS_ALGORITHM)
DEFAULT_ISSUER = APP_CODE

CLOUD_TOKEN_HEADER = 'Cloud-Token'

DEFAULT_ID = '00000000-0000-0000-0000-000000000000'
DEFAULT_UUID = UUID(DEFAULT_ID)

SLUG_TOKEN_LENGTH = 16
ORIGIN_LENGTH = 32

ANONYMOUS = 'anonymous'

SQLITE_DIALECT = 'sqlite3'

DEFAULT_AUTH = 'local'
DEFAULT_OAUTH2ACF = 'oauth2acf'

SECRET_DUMMY = '********'

# TODO: поддержать потоковую загрузку изображений (аналогично файлам в облаке)
STREAM_FILETYPE = 'application/octet-stream'
SUPPORTED_PICTURE_STREAMS = (STREAM_FILETYPE, 'image/png', 'image/jpeg', 'image/webp')
SUPPORTED_PICTURES = ('webp', 'png', 'jpeg', 'jpg')

IMPORT_RE = re.compile(r'^\.*[a-z]+[\.0-9a-z_]+[0-9a-z]+$')

JSON_VALIDATOR = Draft202012Validator

JSON_REF_RE = re.compile(r'^(jsonschema:)(([a-z])*\.?([a-z])+\.schema\.v[0-9]+\.json)$')

HASH_RE = re.compile(r'[0-9A-F]{32}', flags=re.IGNORECASE)  # @UndefinedVariable)

MAX_PICTURE_PX = 512

IMAGES_FORMAT = 'WebP'

COPY_RE = re.compile(r'(.*)_copy_(\d+)$')

IP_RE = re.compile(r'(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}')

ORCHESTRATOR_RE = re.compile(r'^orch-(dagster|airflow)-[a-z]$')

RESOLUTION_ERRORS = (
    'No address associated with hostname',
    'Temporary failure in name resolution',
    'Name or service not known',
    'Connection to dwash-catalog timed out',
)

DAGSTER_APP = PosixPath('/opt/dagster')
DAGSTER_HOME = DAGSTER_APP.joinpath('dagster_home')
DAGSTER_ALERTS_ROOT = DAGSTER_HOME.joinpath(ALERTS_PATH)
DAGSTER_REPORTS_ROOT = DAGSTER_HOME.joinpath(REPORTS_PATH)
DAGSTER_SKIPPER_ROOT = DAGSTER_HOME.joinpath(SKIPPER_PATH)
DAGSTER_SWAP_ROOT = DAGSTER_HOME.joinpath(SWAP_PATH)

MODULE_RE = re.compile(r'^[a-z][a-z0-9_]*[a-z0-9]$')

DEFAULT_REPOSITORY_CODE = 'project'
WORKSPACE_CONFIG = 'workspace.yaml'
DEFAULT_REPOSITORY = '__repository__'

TELEGRAM_MESSAGE_LENGTH = 4096
TELEGRAM_GROUP_RATE_LIMIT = '20/minute'
TELEGRAM_BULK_RATE_LIMIT = '30/second'
TELEGRAM_CHAT_RATE_LIMIT = '60/minute'
TELEGRAM_USERNAME_RE = re.compile(r'^@?[a-zA-Z][_a-zA-Z0-9]{4,}$')
TELEGRAM_CHAT_ID_RE = re.compile(r'^-?[0-9]{6,}$')

DEFAULT_SMB_PORT = 445
DEFAULT_STREAM_CHUNK_SIZE = 4096

GENERATED = 'generated'

DEFAULT_REPORT_TIMEOUT = 300

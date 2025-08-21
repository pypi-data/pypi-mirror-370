""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 9, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from typing import Any, Optional
from os import getenv
from time import time
from json import loads
from copy import deepcopy
from typing import Union
from pathlib import PosixPath
from base64 import urlsafe_b64encode
from secrets import token_urlsafe
from hashlib import sha256
from functools import cache
from dotenv import dotenv_values
from cryptography.fernet import Fernet
from polyants.polyhub.constants import SLUG_TOKEN_LENGTH, SECRET_DUMMY, BEARER_TOKEN_HEADER, INTERNAL_TOKEN_PREFIX
from polyants.polyhub.helpers.adapters import to_json
from polyants.polyhub.helpers.http import get_host_name
from polyants.polyhub.helpers.grpcapi import get_fernet_key as grpc_get_fernet_key


def get_slug_token():
    return token_urlsafe(SLUG_TOKEN_LENGTH)


def generate_code_verifier() -> str:
    return token_urlsafe(64)


def generate_code_challenge(verifier: str) -> str:
    digest = sha256(verifier.encode()).digest()
    return urlsafe_b64encode(digest).rstrip(b'=').decode()


@cache
def get_fernet_key():
    return grpc_get_fernet_key()


def get_fernet():
    return Fernet(get_fernet_key())


def encrypt(value):
    return get_fernet().encrypt(bytes(value, 'utf-8')).decode() if value else ''


def decrypt(value: str) -> str:
    try:
        encoded = bytes(value, 'utf-8')
    except TypeError:
        encoded = None

    return get_fernet().decrypt(encoded).decode() if encoded else ''


def _decrypt_secrets(encrypted: Union[dict, list], target: Union[dict, list]):
    """Расшифровывает секретные (secret=True) опции.
    Модифицирует исходный объект.
    """
    if isinstance(encrypted, (dict, list)):
        for idx, key in enumerate(encrypted):
            if isinstance(encrypted, dict):
                if encrypted.get('secret') is True and 'value' in encrypted:
                    target['value'] = loads(decrypt(encrypted['value']))  # pyre-ignore[6]
                else:
                    _decrypt_secrets(encrypted[key], target[key])
            elif isinstance(encrypted, list):
                _decrypt_secrets(encrypted[idx], target[idx])


def mask_secrets(plain):
    """Скрывает секретные (secret=True) опции.
    Значения секретных опций должны быть валидным JSON.
    Модифицирует исходный объект.
    """
    if isinstance(plain, (dict, list)):
        for idx, key in enumerate(plain):
            if isinstance(plain, dict):
                if plain.get('secret') is True and 'value' in plain:
                    plain['value'] = SECRET_DUMMY
                else:
                    mask_secrets(plain[key])
            elif isinstance(plain, list):
                mask_secrets(plain[idx])


def get_masked_secrets_copy(plain):
    copied = deepcopy(plain)
    mask_secrets(copied)

    return copied


def update_secrets(masked, plain, target):
    """Обновляет и шифрует секретные (secret=True) опции.
    Удаленные опции не восстанавливаются.
    Значения секретных опций должны быть валидным JSON.
    Модифицирует исходный объект.
    """
    if isinstance(masked, (dict, list)):
        for idx, key in enumerate(masked):
            if isinstance(masked, dict):
                if masked.get('secret') is True and 'value' in masked:
                    if masked['value'] == SECRET_DUMMY:
                        target['value'] = (
                            plain.get('value', SECRET_DUMMY) if plain and isinstance(plain, dict) else SECRET_DUMMY
                        )
                    else:
                        target['value'] = encrypt(to_json(masked['value']))
                else:
                    update_secrets(
                        masked[key], plain.get(key) if plain and isinstance(plain, dict) else None, target[key]
                    )
            elif isinstance(masked, list):
                update_secrets(
                    masked[idx], plain[idx] if isinstance(plain, list) and len(plain) > idx else None, target[idx]
                )


def get_updated_secrets_copy(masked, plain):
    copied = deepcopy(masked)
    copied_masked = deepcopy(masked)
    copied_plain = deepcopy(plain)
    update_secrets(copied_masked, copied_plain, copied)

    return copied


def get_decrypted_secrets_copy(encrypted: Union[dict, list]) -> Union[dict, list]:
    copied = deepcopy(encrypted)
    _decrypt_secrets(encrypted, copied)

    return copied


@cache
def get_app_secrets(path: Optional[Union[str, PosixPath]] = None) -> dict:
    path = path or '/run/secrets/app'
    return dotenv_values('/run/secrets/app')


@cache
def get_app_secret(name, path: Optional[Union[str, PosixPath]] = None, with_env: bool = False, default: Any = None):
    secret = get_app_secrets(path=path).get(name)
    if with_env and not secret:
        secret = getenv(name)

    return secret or default


def generate_internal_token():
    fernet = get_fernet()
    timestamp = str(time())
    token_data = f"{timestamp}|{get_host_name()}"
    return fernet.encrypt(token_data.encode()).decode()


def get_internal_headers():
    return {BEARER_TOKEN_HEADER: f'{INTERNAL_TOKEN_PREFIX} {generate_internal_token()}'}

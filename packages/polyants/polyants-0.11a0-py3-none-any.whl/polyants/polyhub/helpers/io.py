""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from __future__ import annotations

import re
import json
import stat
import shutil
import os.path
import tempfile

from typing import Callable, BinaryIO, Any
from abc import ABCMeta, abstractmethod
from io import BytesIO
from fnmatch import fnmatch
from pathlib import PosixPath
from contextlib import contextmanager
from dataclasses import dataclass
from pathvalidate import Platform, sanitize_filepath
from smb.base import SharedFile
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
from jsqlib.helpers.common import Tokenizer
from polyants.internal import log
from polyants.polyhub.constants import CLOUD_ROOT, DEFAULT_SMB_PORT, DEFAULT_STREAM_CHUNK_SIZE
from polyants.polyhub.exceptions import IOException
from polyants.polyhub.helpers.mappings import SWAPS
from polyants.polyhub.helpers.adapters import file_to_md5, bytesio_to_md5, to_bytes
from polyants.polyhub.helpers.translit import to_latin
from polyants.polyhub.helpers.crypto import get_slug_token
from polyants.polyhub.helpers.templater import JINJA
from polyants.polyhub.helpers.http import get_host_name


@dataclass
class ReportRecord:
    path: PosixPath = PosixPath('')
    depth: int = 0
    folder: bool | None = False
    symlink: bool = False
    matched: bool = True
    missing: bool = False
    hidden: bool = False
    root: bool = False
    error: bool = False
    slug: str = ''
    message: str = ''


@dataclass
class SMBConfig:
    username: str
    password: str
    share: str
    host: str
    port: int = DEFAULT_SMB_PORT
    schema: str = ''
    domain: str = ''
    root: str = '/'
    localhost: str = get_host_name()
    use_ntlm_v2: bool = True
    sign_options: int = SMBConnection.SIGN_WHEN_SUPPORTED
    is_direct_tcp: bool = True


class SMB:
    def __init__(self, config: SMBConfig):
        self.config = config

    def __enter__(self):
        self.conn = SMBConnection(
            self.config.username,
            self.config.password,
            self.config.localhost,
            self.config.host,
            self.config.domain,
            use_ntlm_v2=self.config.use_ntlm_v2,
            sign_options=self.config.sign_options,
            is_direct_tcp=self.config.is_direct_tcp,
        )
        self.conn.connect(self.config.host, self.config.port)
        return self.conn

    def __exit__(self, exc_type, exc_value, __):
        if exc_type:
            log.debug('exc_type: %s, exc_value: %s', exc_type, exc_value)
        if self.conn:
            self.conn.close()


class Storage(metaclass=ABCMeta):
    def __init__(self, provider):
        self.provider = provider

    @property
    @abstractmethod
    def root(self) -> str | PosixPath: ...

    @abstractmethod
    def get_full_path(self, relative_path: str | PosixPath) -> str | PosixPath: ...

    @abstractmethod
    def is_exists(self, path: str | PosixPath) -> bool: ...

    @abstractmethod
    def is_file(self, path: str | PosixPath) -> bool: ...

    @abstractmethod
    def is_folder(self, path: str | PosixPath) -> bool: ...

    @abstractmethod
    def is_folders_only(self, path: str | PosixPath) -> bool: ...

    @abstractmethod
    def is_material(self, path: str | PosixPath) -> bool: ...

    @abstractmethod
    def delete_file(self, path: str | PosixPath, missing_ok: bool = False) -> None: ...

    @abstractmethod
    def create_folder(self, path: str | PosixPath, parents: bool = False, exist_ok: bool = False) -> None: ...

    @abstractmethod
    def save_file(self, file: Any, path: str | PosixPath) -> None: ...

    @abstractmethod
    def save_stream(self, stream: BinaryIO, path: str | PosixPath) -> None: ...

    @abstractmethod
    def delete_tree(self, path: str | PosixPath, ignore_errors: bool = False) -> None: ...

    @abstractmethod
    def guess_entry_type(self, path: str | PosixPath) -> str: ...

    @abstractmethod
    def get_file_size(self, path: str | PosixPath) -> int: ...

    @abstractmethod
    def get_relative_path(self, path: str | PosixPath, root: str | PosixPath | None = None) -> str | None: ...

    @abstractmethod
    def joinpaths(self, path: str | PosixPath, paths: list) -> str | PosixPath: ...

    @abstractmethod
    def get_file(self, relative_path: str | PosixPath) -> BinaryIO | str | PosixPath: ...

    @abstractmethod
    def get_file_hash(self, path: str | PosixPath) -> str: ...

    @abstractmethod
    def sync(
        self,
        root: PosixPath,
        folder_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        file_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        folder_patterns: list[str] | None = None,
        file_patterns: list[str] | None = None,
        skip_symlinks: bool = False,
        skip_missing: bool = True,
        skip_hidden: bool = True,
        skip_root: bool = True,
        write_report: bool = True,
        max_depth: int = 0,
        relative_root: PosixPath | None = None,
    ) -> list[ReportRecord] | None: ...


class FSStorage(Storage):
    @property
    def root(self) -> str | PosixPath:
        return CLOUD_ROOT

    def get_full_path(self, relative_path: str | PosixPath) -> str | PosixPath:
        return self.joinpaths(self.root, [relative_path])

    def is_exists(self, path: str | PosixPath) -> bool:
        return PosixPath(path).exists()

    def is_file(self, path: str | PosixPath) -> bool:
        return PosixPath(path).is_file()

    def is_folder(self, path: str | PosixPath) -> bool:
        return PosixPath(path).is_dir()

    def is_folders_only(self, path: str | PosixPath) -> bool:
        path = PosixPath(path)
        if not path.is_dir():
            return False
        else:
            return is_only_dirs(path)

    def is_material(self, path: str | PosixPath) -> bool:
        path = PosixPath(path)
        return bool(path and path != PosixPath('.'))

    def delete_file(self, path: str | PosixPath, missing_ok: bool = False) -> None:
        PosixPath(path).unlink(missing_ok=missing_ok)

    def create_folder(self, path: str | PosixPath, parents: bool = False, exist_ok: bool = False) -> None:
        PosixPath(path).mkdir(parents=parents, exist_ok=exist_ok)

    def save_file(self, file: Any, path: str | PosixPath) -> None:
        file.save(path)

    def save_stream(self, stream: BinaryIO, path: str | PosixPath) -> None:
        with open(path, 'wb') as file:
            for chunk in iter(lambda: stream.read(DEFAULT_STREAM_CHUNK_SIZE), b''):
                file.write(chunk)

    def delete_tree(self, path: str | PosixPath, ignore_errors: bool = False) -> None:
        shutil.rmtree(PosixPath(path), ignore_errors=ignore_errors)

    def guess_entry_type(self, path: str | PosixPath) -> str:
        return guess_dir_entry_type(PosixPath(path))

    def get_file_size(self, path: str | PosixPath) -> int:
        return PosixPath(path).stat().st_size

    def get_relative_path(self, path: str | PosixPath, root: str | PosixPath | None = None) -> str | None:
        root = root or self.root
        return str(PosixPath(path).relative_to(root)) if path else None

    def joinpaths(self, path: str | PosixPath, paths: list) -> str | PosixPath:
        return PosixPath(path).joinpath(*paths)

    def get_file(self, relative_path: str | PosixPath) -> BinaryIO | str | PosixPath:
        return self.joinpaths(self.root, [relative_path])

    def get_file_hash(self, path: str | PosixPath) -> str:
        return file_to_md5(path)

    def sync(
        self,
        root: PosixPath,
        folder_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        file_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        folder_patterns: list[str] | None = None,
        file_patterns: list[str] | None = None,
        skip_symlinks: bool = False,
        skip_missing: bool = True,
        skip_hidden: bool = True,
        skip_root: bool = True,
        write_report: bool = True,
        max_depth: int = 0,
        relative_root: PosixPath | None = None,
    ) -> list[ReportRecord] | None:
        return process_folder(
            root,
            folder_handler=folder_handler,
            file_handler=file_handler,
            folder_patterns=folder_patterns,
            file_patterns=file_patterns,
            skip_symlinks=skip_symlinks,
            skip_missing=skip_missing,
            skip_hidden=skip_hidden,
            skip_root=skip_root,
            write_report=write_report,
            max_depth=max_depth,
            relative_root=relative_root,
        )


class SMBStorage(Storage):
    def __init__(self, provider):
        super().__init__(provider)
        provider_options = provider.options or dict()
        options = provider_options.get('storage', dict()).get('options', dict())
        self.config = SMBConfig(
            username=provider.login,
            password=provider.password,
            share=provider.schema,
            host=provider.host,
            port=provider.port or DEFAULT_SMB_PORT,
            domain=options.get('domain', ''),
            root=f'/{provider.db}/' if provider.db else '/',
            use_ntlm_v2=options.get('use_ntlm_v2', True),
            sign_options=options.get('sign_options', SMBConnection.SIGN_WHEN_SUPPORTED),
            is_direct_tcp=options.get('is_direct_tcp', True),
        )

    @property
    def root(self) -> str | PosixPath:
        return '/'

    def get_full_path(self, relative_path: str | PosixPath) -> str | PosixPath:
        log.debug('get_full_path `%s`', relative_path)
        path = str(relative_path).lstrip('.').lstrip('/')
        return self.joinpaths(self.root, [path])

    def _list_path(self, path: str | PosixPath, share: SMBConnection, skip_root=False) -> list:
        path = str(path)
        try:
            result = share.listPath(self.config.share, os.path.dirname(path), pattern=os.path.basename(path))
        except OperationFailure:
            result = list()

        if skip_root:
            result = [i for i in result if i.filename != os.path.basename(path) and i.isDirectory]

        return result

    def _get_by_path(self, path: str | PosixPath) -> SharedFile:
        result = None
        with SMB(config=self.config) as share:
            if found := self._list_path(path, share):
                len_found = len(found)
                if len_found > 1:
                    log.warning('Multiple entries found: %s', found)
                elif len_found == 1:
                    result = found[0]

        return result

    def is_exists(self, path: str | PosixPath) -> bool:
        log.debug('is_exists `%s`', path)
        exists = False
        if self._get_by_path(path):
            exists = True

        return exists

    def is_file(self, path: str | PosixPath) -> bool:
        log.debug('is_file `%s`', path)
        file = False
        if (found := self._get_by_path(path)) and not found.isDirectory:
            file = True

        return file

    def is_folder(self, path: str | PosixPath) -> bool:
        log.debug('is_folder `%s`', path)
        folder = False
        if (found := self._get_by_path(path)) and found.isDirectory:
            folder = True

        return folder

    def _is_only_dirs(self, path: str | PosixPath, share: SMBConnection) -> bool:
        path = str(path)
        for entry in self._list_path(path, share):
            if not entry.isDirectory or (
                entry.isDirectory and not self._is_only_dirs(self.joinpaths(path, [entry.filename]), share)
            ):
                return False

        return True

    def is_folders_only(self, path: str | PosixPath) -> bool:
        log.debug('is_folders_only `%s`', path)
        with SMB(config=self.config) as share:
            try:
                share.listPath(self.config.share, path)
            except OperationFailure:
                return False
            else:
                return self._is_only_dirs(str(path), share)

    def is_material(self, path: str | PosixPath) -> bool:
        log.debug('is_material `%s`', path)
        return bool(path and path != '.')

    def delete_file(self, path: str | PosixPath, missing_ok: bool = False) -> None:
        log.debug('delete_file `%s`, missing_ok: %s', path, missing_ok)
        with SMB(config=self.config) as share:
            try:
                share.deleteFiles(self.config.share, str(path))
            except OperationFailure as e:
                if missing_ok:
                    log.warning('Ошибка удаления файла `%s`: %s', path, e)
                else:
                    raise e

    def create_folder(self, path: str | PosixPath, parents: bool = False, exist_ok: bool = False) -> None:
        log.debug('create_folder `%s`, parents: %s, exist_ok: %s', path, parents, exist_ok)
        create_current = True
        path = str(path)
        with SMB(config=self.config) as share:
            try:
                share.listPath(self.config.share, path)
            except OperationFailure:
                pass
            else:
                if not exist_ok:
                    raise IOException(f'Директория {path} уже существует')
                else:
                    create_current = False

            if parents:
                parent = os.path.dirname(path)
                while parent != '/' and parent != '' and parent != self.root:
                    try:
                        share.listPath(self.config.share, parent)
                    except OperationFailure:
                        share.createDirectory(self.config.share, parent)

                    parent = os.path.dirname(parent)

            if create_current:
                log.debug('creating folder %s', path)
                share.createDirectory(self.config.share, path)

    def save_file(self, file: Any, path: str | PosixPath) -> None:
        log.debug('save_file `%s`, file: %s', path, file)
        with SMB(config=self.config) as share:
            try:
                share.storeFile(self.config.share, path, file)
            except OperationFailure as e:
                log.debug('Ошибка загрузки файла `%s`: %s', path, e)
                raise IOException('Ошибка сохранения файла %s')

    def save_stream(self, stream: BinaryIO, path: str | PosixPath) -> None:
        log.debug('save_stream `%s`', path)
        with tempfile_ctx() as file_copy:
            with file_copy.open(mode='wb') as f:
                for chunk in iter(lambda: stream.read(DEFAULT_STREAM_CHUNK_SIZE), b''):
                    f.write(chunk)
            with file_copy.open(mode='rb') as f:
                self.save_file(f, path)

    def _delete_folder_tree(self, path: str | PosixPath, share: SMBConnection, ignore_errors: bool = False) -> None:
        path = str(path)
        for item in self._list_path(path, share, skip_root=True):
            item_path = self.joinpaths(path, [item.filename])
            if item.isDirectory:
                self._delete_folder_tree(item_path, share, ignore_errors=ignore_errors)
            else:
                try:
                    share.deleteFiles(self.config.share, item_path)
                except OperationFailure as e:
                    log.debug('Ошибка удаления файла `%s`, директории `%s`: %s', item_path, path, e)
                    if not ignore_errors:
                        raise IOException(f'Ошибка удаления файла `{item_path}`, директории `{path}`')

        if path not in ('/', '.', '..', ''):
            try:
                share.deleteDirectory(self.config.share, path)
            except OperationFailure as e:
                log.debug('Ошибка удаления директории `%s`: %s', path, e)
                if not ignore_errors:
                    raise IOException(f'Ошибка удаления директори `{path}`')

    def delete_tree(self, path: str | PosixPath, ignore_errors: bool = False) -> None:
        log.debug('delete_tree `%s`, ignore_errors: %s', path, ignore_errors)
        with SMB(config=self.config) as share:
            self._delete_folder_tree(str(path), share, ignore_errors=ignore_errors)

    def guess_entry_type(self, path: str | PosixPath) -> str:
        log.debug('guess_entry_type `%s`', path)
        result = 'unknown'
        if entry := self._get_by_path(path):
            if entry.isDirectory:
                result = 'folder'
            else:
                result = 'file'

        return result

    def get_file_size(self, path: str | PosixPath) -> int:
        log.debug('get_file_size `%s`', path)
        result = -1
        if (entry := self._get_by_path(path)) and not entry.isDirectory:
            result = entry.file_size

        return result

    def get_relative_path(self, path: str | PosixPath, root: str | PosixPath | None = None) -> str | None:
        log.debug('get_relative_path `%s`, root: %s', path, root)
        result = None
        root = str(root or self.root)
        if path:
            path = str(path)
            if path.startswith(root):
                result = path[len(root) :].lstrip('/')

        return result

    def joinpaths(self, path: str | PosixPath, paths: list) -> str | PosixPath:
        log.debug('joinpaths `%s`, paths: %s', path, paths)
        path = str(path)
        return os.path.join(path, *paths)

    def get_file(self, relative_path: str | PosixPath) -> BinaryIO | str | PosixPath:
        log.debug('get_file `%s`', relative_path)
        f = BytesIO()
        with SMB(config=self.config) as share:
            share.retrieveFile(self.config.share, self.get_full_path(relative_path), f)
        f.seek(0)
        return f

    def get_file_hash(self, path: str | PosixPath) -> str:
        log.debug('get_file_hash `%s`', path)
        return bytesio_to_md5(self.get_file(path))

    def sync(
        self,
        root: PosixPath,
        folder_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        file_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
        folder_patterns: list[str] | None = None,
        file_patterns: list[str] | None = None,
        skip_symlinks: bool = False,
        skip_missing: bool = True,
        skip_hidden: bool = True,
        skip_root: bool = True,
        write_report: bool = True,
        max_depth: int = 0,
        relative_root: PosixPath | None = None,
    ) -> list[ReportRecord] | None:
        raise IOException('Синхронизация хранилища типа SMB не поддерживается')


def get_clean_path(path, as_string=True, strict=True):
    error_msg = f'Путь {path} некорректен. Содержит `.`'

    if './' in str(path):
        raise IOException(error_msg)

    clean = sanitize_filepath(path, platform=Platform.LINUX)

    if strict and clean != path:
        raise IOException(f'Путь {path} невалиден. ')

    if './' in str(clean):
        raise IOException(error_msg)

    return clean if as_string else PosixPath(clean)


def get_relative_path(path, as_string=True):
    return get_clean_path(str(path).strip('.').strip('/'), as_string=as_string)


def get_file_content(path: str | PosixPath, as_json=False, as_bytes=False):
    content = b'' if as_bytes else ''
    path = PosixPath(path)

    if path.is_file():
        try:
            content = path.read_bytes() if as_bytes else path.read_text()
        except Exception as e:
            raise IOException(f'Не удалось получить содержимое {path}, ошибка: {e}')

    return json.loads(content.decode() if as_bytes else content) if content and as_json else content  # pyre-ignore[16]


def get_safe_name(name):
    """Перекодирует наименование в более удобное при обработке в файловой системе.
    TODO: желательно добавить возможность отключения по настройке или даже несколько уровней.
    """
    name = to_latin(get_clean_path(name))
    safe_re = re.compile(r'[^a-zа-я0-9-]', re.IGNORECASE)  # @UndefinedVariable
    return safe_re.sub('_', name)


def get_safe_path(path):
    result = None

    if path:
        path = get_relative_path(path)
        result = '/'.join([get_safe_name(i) for i in path.split('/')])

    return result


def get_joined_path(parent, child):
    parent = f'{get_relative_path(parent)}/' if parent else ''
    child = get_relative_path(child) if child else ''

    return f'{parent}{child}'


def render_text(text, binds=None):
    if binds is None:
        binds = dict()

    return JINJA.from_string(text).render(binds)


def render_template(path, binds=None, default=None, as_json=True):
    if not path.is_file():
        if default is not None:
            return default

        raise IOException(f'Не найден файл шаблона {path}')

    template = path.read_text()

    try:
        rendered = render_text(template, binds=binds)
    except Exception as e:
        log.error('Ошибка рендеринга: %s\nФайл: %s\nПеременные: %s\n Шаблон: %s', e, path, template, binds)
        raise e

    log.debug('Результат рендеринга %s: %s', path, rendered)

    return json.loads(rendered) if as_json else rendered


def set_file_content(path: str | PosixPath, content, as_json=False, as_bytes=False, create_dirs=False):
    path = PosixPath(path)
    if create_dirs:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise IOException(f'Не удалось создать директорию {path}, ошибка: {e}')

    content = json.dumps(content) if as_json else content
    try:
        content = path.write_bytes(content) if as_bytes else path.write_text(content)
    except Exception as e:
        raise IOException(f'Не удалось записать данные в {path}, ошибка: {e}')


def render_jsql(raw, arguments=None, as_json=True):
    arguments = arguments or dict()
    raw = json.dumps(raw) if isinstance(raw, (dict, list)) else raw
    rendered = Tokenizer(constants=arguments).stringify(raw)

    return json.loads(rendered) if as_json else rendered


def render_mock(raw, arguments=None, as_json=True):
    raw = json.dumps(raw) if isinstance(raw, (dict, list)) else raw
    arguments = arguments or dict()

    for k, v in arguments.items():
        raw = raw.replace(f'"{k}"', v)

    return json.loads(raw) if as_json else raw


def guess_dir_entry_type(entry: PosixPath, follow_symlinks=True) -> str:
    try:
        stat_info = entry.stat(follow_symlinks=follow_symlinks)
    except Exception:
        result = 'unknown'
    else:
        match stat.S_IFMT(stat_info.st_mode):
            case stat.S_IFLNK:
                result = 'symlink'
            case stat.S_IFSOCK:
                result = 'socket'
            case stat.S_IFIFO:
                result = 'pipe'
            case stat.S_IFCHR:
                result = 'chardev'
            case stat.S_IFBLK:
                result = 'blockdev'
            case stat.S_IFREG:
                result = 'file'
            case stat.S_IFDIR:
                result = 'folder'
            case _:
                result = 'unknown'

    return result


def is_broken_path(path: PosixPath) -> bool:
    try:
        path.resolve(strict=True)
        return False
    except FileNotFoundError:
        return True


def is_hidden_path(path: PosixPath) -> bool:
    if path.name.startswith('.'):
        return True
    return False


def rec_record(
    report: list[ReportRecord] | None,
    record: ReportRecord | None,
    relative_root: PosixPath | None = None,
    write_report: bool = True,
) -> None:
    if write_report and record and report is not None:
        if relative_root and record.path:
            record.path = record.path.relative_to(relative_root)
        report.append(record)


def get_path_depth(path: PosixPath, relative_root: PosixPath | None) -> int:
    """Вычисляет глубину пути.
    Уровень содержимого relative_root - 0.
    """
    if relative_root:
        path = path.relative_to(relative_root)
        print(f'{path=}, {len(path.parts)=}')

    return len(path.parts) - 1


def process_folder(
    root: PosixPath,
    folder_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
    file_handler: Callable[[PosixPath, int], ReportRecord | None] | None = None,
    folder_patterns: list[str] | None = None,
    file_patterns: list[str] | None = None,
    skip_symlinks: bool = False,
    skip_missing: bool = True,
    skip_hidden: bool = True,
    skip_root: bool = True,
    write_report: bool = True,
    max_depth: int = 0,
    relative_root: PosixPath | None = None,
) -> list[ReportRecord] | None:
    stack = list()
    report = list() if write_report else None
    current_depth = get_path_depth(root, relative_root=relative_root)

    if skip_symlinks and root.is_symlink():
        rec_record(
            report,
            ReportRecord(root, depth=current_depth, folder=root.is_dir(), symlink=True, root=True),
            relative_root=relative_root,
            write_report=write_report,
        )
        return report

    if skip_missing and is_broken_path(root):
        rec_record(
            report,
            ReportRecord(root, depth=current_depth, folder=root.is_dir(), missing=True, root=True),
            relative_root=relative_root,
            write_report=write_report,
        )
        return report

    if skip_hidden and is_hidden_path(root):
        rec_record(
            report,
            ReportRecord(root, depth=current_depth, folder=root.is_dir(), hidden=True, root=True),
            relative_root=relative_root,
            write_report=write_report,
        )
        return report

    if root.is_dir():
        stack.append(root)

        while stack:
            current = stack.pop()

            if folder_handler:
                if current == root:
                    if skip_root:
                        rec_record(
                            report,
                            ReportRecord(root, depth=current_depth, folder=True, root=True),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                    else:
                        rec_record(
                            report,
                            folder_handler(root, current_depth),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                else:
                    current_depth = get_path_depth(current, relative_root=relative_root)
                    if max_depth == 0 or current_depth <= max_depth:
                        rec_record(
                            report,
                            folder_handler(current, current_depth),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                    else:
                        rec_record(
                            report,
                            ReportRecord(current, depth=current_depth, folder=True),
                            relative_root=relative_root,
                            write_report=write_report,
                        )

            for entry in current.iterdir():
                current_depth = get_path_depth(entry, relative_root=relative_root)

                if max_depth == 0 or current_depth <= max_depth:
                    if skip_symlinks and entry.is_symlink():
                        rec_record(
                            report,
                            ReportRecord(entry, depth=current_depth, folder=entry.is_dir(), symlink=True),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                        continue

                    if skip_missing and is_broken_path(entry):
                        rec_record(
                            report,
                            ReportRecord(entry, depth=current_depth, folder=entry.is_dir(), missing=True),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                        continue

                    if skip_hidden and is_hidden_path(entry):
                        rec_record(
                            report,
                            ReportRecord(entry, depth=current_depth, folder=entry.is_dir(), hidden=True),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                        continue

                    if entry.is_dir():
                        if folder_patterns is None:
                            stack.append(entry)
                        else:
                            for pattern in folder_patterns:
                                if fnmatch(entry.name, pattern):
                                    stack.append(entry)
                                    break
                            else:
                                rec_record(
                                    report,
                                    ReportRecord(entry, depth=current_depth, folder=True, matched=False),
                                    relative_root=relative_root,
                                    write_report=write_report,
                                )
                    elif entry.is_file():
                        if file_handler is not None:
                            if file_patterns is None:
                                rec_record(
                                    report,
                                    file_handler(entry, current_depth),
                                    relative_root=relative_root,
                                    write_report=write_report,
                                )
                            else:
                                for pattern in file_patterns:
                                    if fnmatch(entry.name, pattern):
                                        rec_record(
                                            report,
                                            file_handler(entry, current_depth),
                                            relative_root=relative_root,
                                            write_report=write_report,
                                        )
                                        break
                                else:
                                    rec_record(
                                        report,
                                        ReportRecord(entry, depth=current_depth, matched=False),
                                        relative_root=relative_root,
                                        write_report=write_report,
                                    )
                    elif write_report:
                        rec_record(
                            report,
                            ReportRecord(
                                entry,
                                depth=current_depth,
                                error=True,
                                message=f'Unsupported entry type: {guess_dir_entry_type(entry)}',
                            ),
                            relative_root=relative_root,
                            write_report=write_report,
                        )
                else:
                    rec_record(
                        report,
                        ReportRecord(current, depth=current_depth),
                        relative_root=relative_root,
                        write_report=write_report,
                    )
    else:
        rec_record(
            report,
            ReportRecord(root, depth=current_depth, root=True),
            relative_root=relative_root,
            write_report=write_report,
        )

    return report


def is_only_dirs(path: PosixPath | str) -> bool:
    """Возвращает True, только если все объекты в директории тоже директории."""
    for entry in PosixPath(path).iterdir():
        if entry.is_file() or (entry.is_dir() and not is_only_dirs(entry)):
            return False

    return True


def get_swap_folder(hostname: str | None = None, create=False) -> PosixPath:
    hostname = hostname or get_host_name()
    path = SWAPS[hostname]

    if create:
        path.mkdir(parents=True, exist_ok=True)

    return path


def get_shared_tmp_folder(hostname: str | None = None, create=False) -> PosixPath:
    path = get_swap_folder(hostname).joinpath('tmp')

    if create:
        path.mkdir(parents=True, exist_ok=True)

    return path


def get_storage(provider):
    options = provider.options or dict()
    storage = options.get('storage', dict())
    type_ = storage.get('type', 'fs').lower()
    return {'fs': FSStorage, 'smb': SMBStorage}[type_](provider)


def get_extension(path: str | PosixPath) -> str:
    return os.path.splitext(str(path))[-1]


def create_tempfile(name, content=None, folder=None, mode='w'):
    folder = PosixPath(folder or tempfile.gettempdir())
    path = folder / name
    if content:
        with path.open(mode=mode) as f:
            f.write(content)

    return path


@contextmanager
def tempfile_ctx(name=None, content=None, folder=None, keep_folder=False, binary=False):
    content = to_bytes(content) if content is not None and binary else content
    mode = 'wb' if binary else 'w'
    name = name or get_slug_token()
    path = create_tempfile(name, content=content, folder=folder, mode=mode)
    log.debug('Создан временный файл: %s', path)

    try:
        yield path
    finally:
        if keep_folder:
            path.unlink(missing_ok=True)
        else:
            shutil.rmtree(path.parent, ignore_errors=True)
        log.debug('Временный файл: %s удален', path)

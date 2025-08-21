""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 14, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from base64 import b64decode
from polyants.polyhub.enums import ReportType, ReportInstanceFormat
from polyants.polyhub.helpers.mappings import ROOTS
from polyants.polyhub.helpers.adapters import fix_base64_padding, to_plain_json
from polyants.polyhub.helpers.io import get_relative_path, render_template
from polyants.polyhub.helpers.http import get_host_name
from polyants.polyhub.helpers.data import populate_fields

DATASET_DIR = 'dataset'
OUT_DIR = 'out'
STATIC_DIR = 'static'
INCLUDE_DIR = 'include'
PARAMETERS_EXT = '.parameters'
JASPER_EXT = '.jasper'
DEFINITION_EXT = '.definition'


def get_relative_tree(tree):
    return get_relative_path(tree)


def get_relative_name(tree):
    return get_relative_tree(tree).rsplit('/', maxsplit=1)[-1]


def get_root(tree):
    root = ROOTS[get_host_name()]
    return root.joinpath(get_relative_tree(tree))


def get_basename(tree):
    return str(get_relative_name(tree))


def get_filename(tree, format_: ReportInstanceFormat):
    return f'{get_basename(tree)}.{format_.value}'


def get_compiled_name(id_, type_: ReportType):
    return f'{id_}.jasper' if type_ == ReportType.JRXML else ''


def get_dirpath(tree, type_: ReportType):
    return get_root(tree).joinpath(type_.value)


def get_dirpath_child(tree, type_: ReportType, name: str):
    return get_dirpath(tree, type_).joinpath(name)


def get_out_dirpath(tree, type_: ReportType):
    return get_dirpath_child(tree, type_, OUT_DIR)


def get_dataset_dirpath(tree, type_: ReportType):
    return get_dirpath_child(tree, type_, DATASET_DIR)


def get_static_dirpath(tree, type_: ReportType):
    path = None
    if type_ in (ReportType.JRXML, ReportType.HTML):
        path = get_dirpath_child(tree, type_, STATIC_DIR)

    return path


def get_include_dirpath(tree, type_: ReportType):
    return get_dirpath_child(tree, type_, INCLUDE_DIR)


def get_template_path(id_, tree, type_: ReportType):
    return get_dirpath(tree, type_).joinpath(f'{id_}.{type_.value}')


def get_parameters_path(id_, tree, type_: ReportType):
    return get_dirpath(tree, type_).joinpath(f'{id_}{PARAMETERS_EXT}')


def get_compiled_path(id_, tree, type_: ReportType):
    return get_dirpath(tree, type_).joinpath(f'{id_}{JASPER_EXT}')


def get_definition_path(id_, tree, type_: ReportType):
    return get_dirpath(tree, type_).joinpath(f'{id_}{DEFINITION_EXT}')


def get_instance_out_dirpath(tree, type_: ReportType, hash_):
    return get_out_dirpath(tree, type_).joinpath(str(hash_))


def get_instance_dataset_path(tree, type_: ReportType, hash_):
    path = None
    if type_ == ReportType.JRXML:
        path = get_dataset_dirpath(tree, type_).joinpath(f'.{hash_}.json')

    return path


def get_instance_static_path(tree, type_: ReportType, hash_):
    path = None
    dirpath = get_static_dirpath(tree, type_)
    if dirpath:
        path = dirpath.joinpath(str(hash_))

    return path


def decode_origin(origin: str) -> str:
    fixed = fix_base64_padding(origin)
    return b64decode(fixed, validate=True).decode('utf-8')


def get_definition(report_id, tree, type_, arguments=None):
    definition_path = get_definition_path(report_id, tree, type_)
    arguments = arguments or dict()
    definition = dict()

    if definition_path.exists():
        definition = to_plain_json(render_template(definition_path, binds=arguments))

    return definition


def get_parameters(id_, tree, type_, user_id: str, provider: dict | None = None):
    """Возвращает список параметров переданного отчета."""
    parameters = to_plain_json(render_template(get_parameters_path(id_, tree, type_), default=list()))
    return populate_fields(parameters, user_id, provider=provider)

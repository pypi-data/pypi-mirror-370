""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from enum import IntFlag, Enum, auto


class AutoValueEnum(Enum):
    def _generate_next_value_(self, start, count, last_values):
        """Возвращает значение в camelCase,
        преобразуя `_x` в прописные буквы,
        остальные - в строчные.
        """
        value = self
        converted = list()
        upper = False

        for c in value:
            if c == '_':
                upper = True
                continue

            if upper:
                converted.append(c.upper())
                upper = False
            else:
                converted.append(c.lower())

        return ''.join(converted)


class ReportInstanceFormat(AutoValueEnum):
    DOCX = auto()
    HTML = auto()
    PDF = auto()
    PPTX = auto()
    RTF = auto()
    XLS = auto()
    XLSX = auto()
    TXT = auto()


class GenericState(IntFlag):
    """Перечисление состояний типового объекта.
    Индивидуальные перечисления состояний должны включать его элементы.
    """

    UNKNOWN = 0
    DELETED = auto()
    ACTIVE = auto()
    INVALID = auto()


class AuthType(AutoValueEnum):
    LOCAL = auto()
    LDAP = auto()
    OAUTH = auto()
    VISIOLOGY = auto()


class ProviderType(AutoValueEnum):
    LOCAL = auto()  # fs
    JSON = auto()  # db (INTERNAL)
    POSTGRESQL = auto()
    MSSQL = auto()
    VIQUBE = auto()
    HTTP = auto()
    HTTPS = auto()
    DWH = auto()  # Polyflow
    EMAIL = auto()
    TELEGRAM = auto()
    MONGO = auto()
    PLAINFS = auto()


class AccessrightType(IntFlag):
    UNKNOWN = 0
    READ = auto()  # 1
    WRITE = auto()  # 2
    EXECUTE = auto()  # 4
    MANAGE = auto()  # 8
    CREATE = auto()  # 16
    ACTIVATE = auto()  # 32


class ReportType(AutoValueEnum):
    DOCX = auto()
    JRXML = auto()
    XLSX = auto()
    HTML = auto()


class PermissionScope(AutoValueEnum):
    GROUP = auto()
    OBJECT = auto()


class CloudObjectType(AutoValueEnum):
    NODE = auto()
    FOLDER = auto()
    FILE = auto()


class EntryOperation(AutoValueEnum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


class TaskType(AutoValueEnum):
    QUEUE = auto()
    ASYNC = auto()


class ScheduleType(AutoValueEnum):
    INTERVAL = auto()
    TIMEDELTA = auto()
    CRONTAB = auto()
    SOLAR = auto()


class DwhFamily(AutoValueEnum):
    MODELS = auto()
    RULES = auto()


class BucketCapability(AutoValueEnum):
    LIST_FILES = auto()
    READ_FILES = auto()
    WRITE_FILES = auto()
    DELETE_FILES = auto()
    SYNC_FILES = auto()


class DatagridCapability(AutoValueEnum):
    READ_ENTRIES = auto()
    ADD_ENTRIES = auto()
    EDIT_ENTRIES = auto()
    DELETE_ENTRIES = auto()


class ReportCapability(AutoValueEnum):
    LIST_INSTANCES = auto()
    READ_INSTANCES = auto()
    WRITE_INSTANCES = auto()
    DELETE_INSTANCES = auto()


class AlertCapability(AutoValueEnum):
    EXECUTE_TRIGGER = auto()


class WorkflowCapability(AutoValueEnum):
    EXECUTE_TRIGGER = auto()


class DwhruleCapability(AutoValueEnum):
    EXECUTE_TRIGGER = auto()


class ProductCapability(AutoValueEnum):
    EXECUTE_TRIGGER = auto()


class OrchestratorCore(AutoValueEnum):
    DAGSTER = auto()
    AIRFLOW = auto()


class EventType(IntFlag):
    UNKNOWN = 0
    MANAGE = auto()  # 1
    CREATE = auto()  # 2
    EXECUTE = auto()  # 4
    PERMIT = auto()  # 8
    FORBID = auto()  # 16
    TWEAK = auto()  # 32
    UPDATE = auto()  # 64
    ACTIVATE = auto()  # 128
    DEACTIVATE = auto()  # 256
    DELETE = auto()  # 512
    RESTORE = auto()  # 1024
    PURGE = auto()  # 2048
    EDIT = auto()  # 4096
    LOGIN = auto()  # 8192
    LOGOUT = auto()  # 16384
    STREAM = auto()  # 32768
    UPLOAD = auto()  # 65536
    DOWNLOAD = auto()  # 131072


class ObjectType(IntFlag):
    """Тип объекта (Класс).
    Все управляемые, т.е. поддерживающие настройки и разрешения, типы объектов должны быть в этом перечислении.
    Битовые комбинации позволяют привязку настроек сразу к нескольким типам объектов (без object_id).
    """

    UNKNOWN = 0
    SYSTEM = auto()  # 1
    USER = auto()  # 2
    GROUP = auto()  # 4
    ACCESSRIGHT = auto()  # 8
    SETTING = auto()  # 16
    PROVIDER = auto()  # 32
    REPORT = auto()  # 64
    BUCKET = auto()  # 128
    DATAGRID = auto()  # 256
    JSONSCHEMA = auto()  # 512
    DWHMODEL = auto()  # 1024
    TASK = auto()  # 2048
    SCHEDULE = auto()  # 4096
    DWHRULE = auto()  # 8192
    WINDOW = auto()  # 16384
    ALERT = auto()  # 32768
    FILLER = auto()  # 65536
    ORCHESTRATOR = auto()  # 131072
    DUMMY = auto()  # 262144
    SCRIPT = auto()  # 524288
    REPOSITORY = auto()  # 1048576
    PRODUCT = auto()  # 2097152
    WORKFLOW = auto()  # 4194304


class ScriptType(AutoValueEnum):
    PYTHON = auto()
    SQL = auto()
    SH = auto()


class AlertFormat(AutoValueEnum):
    TXT = auto()
    HTML = auto()
    MD = auto()


class ReportInstancePhase(AutoValueEnum):
    REQUESTED = auto()
    QUEUED = auto()
    GENERATING = auto()
    GENERATED = auto()
    POPULATING = auto()
    POPULATED = auto()
    DISCARDED = auto()
    FAILED = auto()


class ProductPhase(AutoValueEnum):
    PENDING = auto()
    COMPLETED = auto()
    APPROVED = auto()
    REJECTED = auto()
    FAILED = auto()


class AlertInstancePhase(AutoValueEnum):
    REQUESTED = auto()
    STARTED = auto()
    FINISHED = auto()
    FAILED = auto()


class DwhruleInstancePhase(AutoValueEnum):
    REQUESTED = auto()
    STARTED = auto()
    PASSED = auto()
    MISSED = auto()
    FINISHED = auto()
    FAILED = auto()


class WorkflowInstancePhase(AutoValueEnum):
    REQUESTED = auto()
    STARTED = auto()
    STOPPED = auto()
    FINISHED = auto()
    FAILED = auto()

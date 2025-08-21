""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from typing import NamedTuple
from uuid import UUID
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from polyants.polyhub.constants import BACK_CODE, API_SLUG
from polyants.polyhub.enums import ObjectType, WorkflowInstancePhase, AlertInstancePhase
from polyants.polyhub.helpers.common import get_type_object_class, get_now
from polyants.polyhub.helpers.adapters import to_json, to_base64, from_base64
from polyants.polyhub.helpers.crypto import get_internal_headers
from polyants.polyhub.helpers.http import get_api_host_url


class ResolvedGlobalId(NamedTuple):

    type: str
    id: str


def _serialize(value: str | int) -> str | bytes:
    return value if isinstance(value, str) else str(value)


def _to_global_id(type_: str, id_: str | int) -> str | bytes:
    return to_base64(f"{type_}:{_serialize(id_)}")


def _from_global_id(global_id: str) -> ResolvedGlobalId:
    "" "Возваращает тип и идентификатор из глобального id. " ""
    global_id = from_base64(global_id, encode_encoding='ascii')
    if ":" not in global_id:
        return ResolvedGlobalId("", global_id)

    return ResolvedGlobalId(*global_id.split(":", 1))


def to_local_id(global_id, decoded=False, as_guid=True, default=None):
    """Конвертирует глобальный Id GraphQL в Id объекта БД."""
    local_id = default or None

    if global_id:
        try:
            if decoded:
                local_id = str(global_id).split(':', 1)[-1]
            else:
                local_id = _from_global_id(global_id)[-1]

            local_id = UUID(local_id) if as_guid else local_id
        except (ValueError, TypeError, IndexError):
            pass

    return local_id


def to_raw_global_id(type_, local_id):
    """Конвертирует Id объекта БД в глобальный Id GraphQL без кодирования в base64.
    Пример: Setting:421bb829-cc47-4ca3-926e-ca19e8191966
    """
    result = None

    if type_ and local_id:
        result = f'{type_}:{local_id}'

    return result


def to_global_id(type_, local_id):
    """Конвертирует Id объекта БД в глобальный Id GraphQL.
    Пример: U2V0dGluZzo0MjFiYjgyOS1jYzQ3LTRjYTMtOTI2ZS1jYTE5ZTgxOTE5NjY=
    """
    global_id = None
    if type_ and local_id:
        global_id = _to_global_id(type_, local_id)

    return global_id


def get_client(code):
    if code == BACK_CODE:
        url = f'{get_api_host_url(code)}/{API_SLUG}/graphql'
    else:
        url = f'{get_api_host_url(code)}/graphql'

    headers = {'Content-Type': 'application/json'} | get_internal_headers()

    return Client(transport=RequestsHTTPTransport(url=url, headers=headers, verify=False))


def execute(query, params=None, client_code=BACK_CODE):
    return get_client(client_code).execute(gql(query), variable_values=params)


def recycle_local_cloud(user_id=None, bucket_ids=None):
    """Физически удаляет DELETED объекты BucketObject и освободившиеся связанные CloudObject."""
    params = dict()
    query = '''mutation($input: InternalBucketRecycleInput!){
    internal {
        bucket {
            recycle(input: $input) {
                payload {
                    affected
                }
            }
        }
    }
}
'''
    params['input'] = {'bucketIds': bucket_ids} if bucket_ids else dict()
    if user_id:
        params['input']['userId'] = user_id

    return execute(query, params=params)


def trigger_execute(object_type: ObjectType, object_id: str, user_id: str, arguments: dict | None = None):
    name = get_type_object_class(object_type)
    query = f'''mutation($input: Internal{name}TriggerInput!){{
    internal {{
        {name.lower()} {{
            trigger(input: $input) {{
                ok
                errors {{
                    ... on ErrorInterface {{
                        code
                        message
                        field
                    }}
                }}
            }}
        }}
    }}
}}
'''
    params = {
        "input": {
            f"{name.lower()}Id": object_id,
            "userId": user_id,
        }
    }
    if arguments:
        packed = list()
        for k, v in arguments.items():
            # пока передаем без типа, автоматически формируя список UniMap
            item = {'name': k, 'body': to_json({'value': v})}
            packed.append(item)

        params['input']['arguments'] = packed  # pyre-ignore[6]

    return execute(query, params=params)


def trigger_alert(alert_id: str, user_id: str, arguments: dict | None = None):
    return trigger_execute(ObjectType.ALERT, alert_id, user_id, arguments=arguments)


def trigger_workflow(workflow_id: str, user_id: str, arguments: dict | None = None):
    return trigger_execute(ObjectType.WORKFLOW, workflow_id, user_id, arguments=arguments)


def trigger_advance(
    object_type: ObjectType,
    object_id: str,
    instance_id: int,
    phase: WorkflowInstancePhase | AlertInstancePhase,
    note: str = '',
):
    name = get_type_object_class(object_type)
    query = f'''mutation($input: Internal{name}AdvanceInput!){{
    internal {{
        {name.lower()} {{
            advance(input: $input) {{
                ok
                errors {{
                    ... on ErrorInterface {{
                        code
                        message
                        field
                    }}
                }}
            }}
        }}
    }}
}}
'''
    params = {"input": {f'{name.lower()}Id': object_id, 'instanceId': instance_id, 'phase': phase, 'note': note}}

    return execute(query, params=params)


def advance_alert(alert_id: str, instance_id: int, phase: AlertInstancePhase, note: str = ''):
    return trigger_advance(ObjectType.ALERT, alert_id, instance_id, phase, note=note)


def advance_workflow(workflow_id: str, instance_id: int, phase: WorkflowInstancePhase, note: str = ''):
    return trigger_advance(ObjectType.ALERT, workflow_id, instance_id, phase, note=note)


def progress_bucket(
    workflow_id: str, flow: dict, bucket_id: str | None = None, slug: str | None = None, timestamp: bool = True
):
    query = '''mutation($input: InternalBucketProgressInput!){
    internal {
        bucket {
            progress(input: $input) {
                ok
                errors {
                    ... on ErrorInterface {
                        code
                        message
                        field
                    }
                }
            }
        }
    }
}
'''
    if timestamp and 'timestamp' not in flow:
        flow['timestamp'] = get_now()
    params = {'input': {'workflowId': workflow_id, 'flow': to_json(flow), 'bucketId': bucket_id, 'slug': slug}}

    return execute(query, params=params)

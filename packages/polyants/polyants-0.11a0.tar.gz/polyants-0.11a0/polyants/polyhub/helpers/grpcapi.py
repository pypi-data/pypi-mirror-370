""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 13, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import grpc

from functools import cache
from polyants.polyhub.constants import ORIGIN_HOST
from polyants.polyhub.grpc import origincrypto_pb2, origincrypto_pb2_grpc, originhttp_pb2, originhttp_pb2_grpc


@cache
def get_fernet_key() -> str:
    with grpc.insecure_channel(ORIGIN_HOST) as channel:
        stub = origincrypto_pb2_grpc.OriginCryptoStub(channel)
        response = stub.GetFernetKey(origincrypto_pb2.Empty())

    return response.value


@cache
def get_protocol() -> str:
    with grpc.insecure_channel(ORIGIN_HOST) as channel:
        stub = originhttp_pb2_grpc.OriginHttpStub(channel)
        response = stub.GetProtocol(originhttp_pb2.Empty())

    return response.value

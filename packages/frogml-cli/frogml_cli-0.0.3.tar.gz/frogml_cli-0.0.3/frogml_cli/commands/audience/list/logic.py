from typing import List

import grpc
from frogml._proto.qwak.audience.v1.audience_pb2 import AudienceEntry
from frogml.core.clients.audience import AudienceClient

from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound


def list_audience() -> List[AudienceEntry]:
    try:
        return AudienceClient().list_audience()
    except grpc.RpcError as e:
        if e.args[0].code == grpc.StatusCode.NOT_FOUND:
            raise FrogmlResourceNotFound(e.args[0].details)
        raise FrogmlCommandException(e.args[0].details)

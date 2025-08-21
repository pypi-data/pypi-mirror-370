import grpc
from frogml.core.clients.audience import AudienceClient

from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound


def delete_audience(audience_id: str) -> None:
    try:
        AudienceClient().delete_audience(audience_id=audience_id)
    except grpc.RpcError as e:
        if e.args[0].code == grpc.StatusCode.NOT_FOUND:
            raise FrogmlResourceNotFound(e.args[0].details)
        raise FrogmlCommandException(e.args[0].details)

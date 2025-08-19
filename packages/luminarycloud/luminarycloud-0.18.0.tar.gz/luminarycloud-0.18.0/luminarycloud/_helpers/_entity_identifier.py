from uuid import uuid4
from luminarycloud._proto.client.entity_pb2 import EntityIdentifier


def _create_entity_identifier() -> EntityIdentifier:
    return EntityIdentifier(id=str(uuid4()), name="")

from .._proto.base.base_pb2 import AdFloatType

from ..types.adfloat import _to_ad_proto, _from_ad_proto
from ..types import LcFloat


def _named_variables_to_proto(
    named_variables: dict[str, LcFloat],
) -> dict[str, AdFloatType]:
    return {k: (_to_ad_proto(v)) for k, v in named_variables.items()}


def _named_variables_from_proto(
    named_variables: dict[str, AdFloatType],
) -> dict[str, LcFloat]:
    return {k: _from_ad_proto(v) for k, v in named_variables.items()}

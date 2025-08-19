# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from os import PathLike
from typing import Union

from google.protobuf.json_format import Parse, ParseDict

from .._proto.client.simulation_pb2 import SimulationParam


def simulation_params_from_json(text: Union[str, bytes]) -> SimulationParam:
    return Parse(text, SimulationParam(), ignore_unknown_fields=True)


def simulation_params_from_json_dict(data: dict) -> SimulationParam:
    return ParseDict(data, SimulationParam(), ignore_unknown_fields=True)


def simulation_params_from_json_path(json_path: PathLike | str) -> SimulationParam:
    with open(json_path, "rb") as fp:
        json_bytes = fp.read()
    return simulation_params_from_json(json_bytes)

# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta


def timestamp_to_datetime(ts: Timestamp) -> datetime:
    return datetime.utcfromtimestamp(ts.seconds) + timedelta(microseconds=ts.nanos / 1000)

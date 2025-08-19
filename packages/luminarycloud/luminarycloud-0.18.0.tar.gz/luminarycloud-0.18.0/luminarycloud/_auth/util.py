# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.

import hashlib
import secrets
import socket
from base64 import urlsafe_b64encode
from datetime import datetime
from time import mktime
from typing import Any

import jwt


def auth0_url_encode(byte_data: bytes) -> str:
    """
    Safe encoding handles + and /, and also replace = with nothing
    :param byte_data:
    :return:
    """
    return urlsafe_b64encode(byte_data).decode("utf-8").replace("=", "")


def generate_nonce() -> str:
    return auth0_url_encode(secrets.token_bytes(32))


def sha256_challenge(verifier: str) -> str:
    return auth0_url_encode(hashlib.sha256(verifier.encode()).digest())


def unix_timestamp_now() -> int:
    return int(mktime(datetime.now().timetuple()))


def decode_jwt(jwt_token: str) -> dict[str, Any]:
    return jwt.decode(jwt_token, options={"verify_signature": False})


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

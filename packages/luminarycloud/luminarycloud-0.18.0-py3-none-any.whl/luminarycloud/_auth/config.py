# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.
import platform
import os
from typing import cast

from dotenv import load_dotenv

load_dotenv()

# Default to the credentials for the prod tenant.
LC_AUTH_DOMAIN = os.getenv("LC_AUTH_DOMAIN") or "luminarycloud-prod.us.auth0.com"
LC_AUTH_CLIENT_ID = os.getenv("LC_AUTH_CLIENT_ID") or "JTsXa4fbArSCl6i9xylUpwrwpovtkss1"
LC_AUTH_SERVICE_ID = os.getenv("LC_AUTH_SERVICE_ID") or "https://apis.luminarycloud.com"

if os.getenv("LC_REFRESH_ROTATION"):
    LC_REFRESH_ROTATION = os.environ["LC_REFRESH_ROTATION"].upper() == "TRUE"
else:
    LC_REFRESH_ROTATION = True

TIMEOUT = 5

# These should match the `allowed_callbacks` field in the Auth0 application configuration.
# https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
ALLOWED_CALLBACK_PORTS = [10001, 9876, 22223, 5000]

LC_CREDENTIALS_DIR = os.getenv("LC_CREDENTIALS_DIR")
if LC_CREDENTIALS_DIR is None:
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        LC_CREDENTIALS_DIR = os.path.expanduser("~/.config/luminarycloud")
    elif system == "Windows" and os.getenv("APPDATA"):
        APPDATA = cast(str, os.getenv("APPDATA"))
        LC_CREDENTIALS_DIR = os.path.join(APPDATA, "Roaming/luminarycloud")

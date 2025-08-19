# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.
import os

from dotenv import load_dotenv

load_dotenv()

# Default to prod.
LC_DOMAIN = os.getenv("LC_DOMAIN") or "apis.luminarycloud.com"
LC_API_KEY = os.getenv("LC_API_KEY")

# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import json
import logging
import os
from typing import Optional

from .config import LC_CREDENTIALS_DIR

logger = logging.getLogger(__name__)


class CredentialsStore:
    """
    Wrapper for a JSON file used to store credentials for use by the SDK.

    If dir is None, it does nothing.
    """

    def __init__(self, dbname: str, dir: Optional[str] = LC_CREDENTIALS_DIR):
        self._path = None
        if dir is not None:
            os.makedirs(dir, exist_ok=True)
            self._path = os.path.join(dir, dbname)

    def _get_store(self) -> dict:
        if self._path is None or not os.path.exists(self._path):
            return {}
        with open(self._path, "r") as store_file:
            store_contents = store_file.read()
        if not store_contents:
            return {}
        return json.loads(store_contents)

    def _write_store(self, store: dict) -> None:
        if self._path is None:
            return
        with open(self._path, "w") as store_file:
            json.dump(store, store_file)

    def save(self, key: str, val: Optional[str]) -> None:
        """Set the value for a key in this store."""
        if self._path is not None:
            logger.info(f"Writing value with key '{key}' to {self._path}.")
            store = self._get_store()
            if val is None:
                del store[key]
            else:
                store[key] = val
            self._write_store(store)

    def recall(self, key: str) -> Optional[str]:
        """Get a value from this store by key."""
        if self._path is not None:
            logger.info(f"Attempting to read value with key '{key}' from {self._path}.")
            store = self._get_store()
            if key in store:
                return store[key]
            logger.info(f"Key not found: {key}.")
        return None

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Hammerheads Engineers sp. z o.o.
# Author: Aleksander Stanik
from spx_python.client import SpxClient
from typing import Optional

__version__ = '0.1.0-rc.3'
__all__ = ['init', 'SpxClient']


def init(
    address: str = "http://localhost:8000",
    product_key: Optional[str] = None,
    **kwargs
) -> SpxClient:
    """
    Initialize the SPX Python client against the SPX server.

    :param address: Base URL of the SPX server (including scheme and port).
    :param product_key: License or product key for authentication.
    :param kwargs: Additional options forwarded to SpxClient.
    :return: Configured SpxClient instance.
    """
    spx_client = SpxClient(base_url=address, product_key=product_key, **kwargs)
    return spx_client

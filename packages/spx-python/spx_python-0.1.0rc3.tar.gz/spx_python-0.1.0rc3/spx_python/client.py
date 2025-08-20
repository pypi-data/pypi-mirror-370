# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Hammerheads Engineers sp. z o.o.
# Author: Aleksander Stanik
"""
SPX Python Client

Dictionary-like interface to SPX Server API v3.
Supports GET and PUT for components and attributes under a named system.
"""
import requests
import json
from collections.abc import MutableMapping


class SpxClient(MutableMapping):
    """
    A client for SPX Server API v3 with dict-like access.

    Usage:
        client = SPXClient(
            base_url='http://127.0.0.1:8000',
            product_key='YOUR_PRODUCT_KEY',
            system_name='your_system'
        )
        # Read an attribute:
        temp = client['timer'].time
        # Set an attribute:
        client['timer'].time = 5.0
        # Get full component or root JSON:
        data = client ['timer'] # returns JSON at current path
    """
    def __init__(self,
                 base_url: str,
                 product_key: str,
                 http_client=None,
                 path: list[str] = None
                 ):
        self.base_url = base_url.rstrip('/')
        self.product_key = product_key
        self.path = path or []
        self.headers = {
            'Authorization': f'Bearer {self.product_key}',
            'Content-Type': 'application/json'
        }
        # allow injection of a custom HTTP client (e.g. FastAPI TestClient)
        self.http = http_client or requests

    def _build_url(self) -> str:
        # Build full URL for current path
        segments = [self.base_url, 'api', 'v3', 'system'] + self.path
        return '/'.join(segments)

    def __getitem__(self, key: str):
        # Extend path and perform GET
        new_path = self.path + [key]
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
        resp = self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        data = resp.json()
        # Leaf attribute returns {'value': ...}
        if isinstance(data, dict) and 'value' in data:
            return data['value']
        # Otherwise return a new client focused on the deeper path
        return SpxClient(self.base_url,
                         self.product_key,
                         http_client=self.http,
                         path=new_path)

    def __setitem__(self, key: str, value):
        # Extend path and perform PUT
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + self.path)
        payload = {key: value}
        resp = self.http.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        # Return JSON response or empty dict
        try:
            return resp.json()
        except ValueError:
            return {}

    def __delitem__(self, key: str):
        # Extend path and perform DELETE
        new_path = self.path + [key]
        url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
        resp = self.http.delete(url, headers=self.headers)
        resp.raise_for_status()
        return None

    def __contains__(self, key: str) -> bool:
        """
        Dictionary-like membership test at the current path.
        Returns True if `key` exists in the JSON data returned by GET.
        """
        data = self.get()
        children = data.get('children', [])
        return any(child.get('name') == key for child in children)

    def get(self):
        """
        GET the full JSON at current path.
        """
        url = self._build_url()
        resp = self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def to_dict(self) -> dict:
        """
        Return the current path's JSON as a pure Python dict.
        """
        return self.get()

    def __repr__(self):
        return f"<SPXClient path={'/'.join(self.path) or '<root>'}>"

    def __eq__(self, other):
        """
        Compare this client's data to another client or dict by comparing
        their JSON structures.
        """
        if isinstance(other, SpxClient):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return False

    def __ne__(self, other):
        """
        Inverse of __eq__ for inequality comparison.
        """
        return not (self == other)

    def __str__(self):
        """
        Return the full system structure from the current path
        as formatted JSON.
        """

        data = self.get()
        return json.dumps(data, indent=2)

    def _call_method(self, method_name, **kwargs):
        url = f"{self._build_url()}/method/{method_name}"
        resp = self.http.post(url, json=kwargs, headers=self.headers)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return None

    def __getattr__(self, key: str):
        # never intercept private/special names
        if key.startswith("_"):
            error_msg = (
                f"{type(self).__name__!r} has no attribute "
                f"{key!r}"
            )
            raise AttributeError(error_msg)
        # fetch raw JSON for this path
        data = object.__getattribute__(self, "get")()
        # top-level simple values
        if key in data and not isinstance(data[key], dict):
            return data[key]
        # look in the 'attr' section
        attr_sec = data.get("attr", {})
        if key in attr_sec:
            return attr_sec[key].get("value")
        # fallback: treat as RPC method
        return lambda **kwargs: self._call_method(key, **kwargs)

    def __setattr__(self, key: str, value):
        """
        Allow setting attributes directly on the client.
        This will set the value in the 'attr' section of the current path.
        """
        if key in ('base_url', 'product_key', 'http', 'path', 'headers'):
            # Handle special attributes
            super().__setattr__(key, value)
        else:
            new_path = self.path + ["attr"] + [key]
            url = '/'.join([self.base_url, 'api', 'v3', 'system'] + new_path)
            payload = {'value': value}
            resp = self.http.put(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            # Return JSON response or empty dict
            try:
                return resp.json()
            except ValueError:
                return {}

    def __iter__(self):
        """
        Iterate over keys in the current mapping:
        attribute names and child component names.
        """
        data = self.get()
        # Only child component names from 'children' list
        child_keys = [child.get('name') for child in data.get('children', [])]
        for key in child_keys:
            yield key

    def __len__(self):
        """
        Return the total number of keys in the mapping.
        """
        data = self.get()
        return len(data.get('attr', {})) + len(data.get('children', []))

    def keys(self):
        return list(self.__iter__())

    def items(self):
        return [(key, self[key]) for key in self]

    def values(self):
        return [self[key] for key in self]

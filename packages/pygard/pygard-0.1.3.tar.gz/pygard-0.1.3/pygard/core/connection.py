# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:59
# @Description:


"""
Connection management for PyGard client.
"""

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import structlog
from typing import Optional, Dict

from ..config import GardConfig
from ..utils import GardConnectionError


class ConnectionManager:
    """Manages HTTP connections and sessions for the Gard client."""

    def __init__(self, config: GardConfig) -> None:
        """
        Initialize connection manager.
        
        Args:
            config: Gard configuration
        """
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self._session: Optional[ClientSession] = None
        self._connector: Optional[TCPConnector] = None

    async def __aenter__(self) -> "ConnectionManager":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the connection manager and create session."""
        if self._session is not None:
            return

        # Create connector with connection pooling
        self._connector = TCPConnector(
            limit=self.config.connection_pool_size,
            limit_per_host=self.config.connection_pool_size,
            keepalive_timeout=self.config.keepalive_timeout,
        )

        # Create timeout configuration
        timeout = ClientTimeout(total=self.config.timeout)

        # Create session
        self._session = ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers=self._get_default_headers(),
        )

        self.logger.info(
            "Connection manager started",
            pool_size=self.config.connection_pool_size,
            timeout=self.config.timeout
        )

    async def close(self) -> None:
        """Close the connection manager and session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

        if self._connector is not None:
            await self._connector.close()
            self._connector = None

        self.logger.info("Connection manager closed")

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "PyGard/0.1.0",
        }

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers

    @property
    def session(self) -> ClientSession:
        """Get the current session."""
        if self._session is None:
            raise GardConnectionError("Connection manager not started")
        return self._session

    def request(self, method: str, url: str, **kwargs):
        """
        Return the aiohttp request context manager.
        """
        if self._session is None:
            raise GardConnectionError("Connection manager not started")

        self.logger.debug(
            "Making request",
            method=method,
            url=url,
            **{k: v for k, v in kwargs.items() if k != "data"}
        )
        return self._session.request(method, url, **kwargs)

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make a GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make a POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make a PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make a DELETE request."""
        return await self.request("DELETE", url, **kwargs)

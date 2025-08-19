# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 13:59
# @Description:


"""
Base service class for PyGard client.
"""

import aiohttp
import structlog
from typing import Any, Dict, Optional, TypeVar, Generic

from ..config import GardConfig
from ..utils import (
    GardException,
    GardConnectionError,
    GardValidationError,
    GardNotFoundError,
    GardAuthenticationError,
    GardRateLimitError,
)
from .connection import ConnectionManager

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class providing common functionality for all services."""

    def __init__(self, connection_manager: ConnectionManager, config: GardConfig) -> None:
        """
        Initialize base service.
        
        Args:
            connection_manager: Connection manager instance
            config: Gard configuration
        """
        self.connection_manager = connection_manager
        self.config = config
        self.logger = structlog.get_logger(self.__class__.__name__)

    async def _handle_response(
            self,
            response: aiohttp.ClientResponse,
            model_class: Optional[type] = None
    ) -> Any:
        """
        Handle HTTP response and convert to appropriate model.
        
        Args:
            response: HTTP response
            model_class: Optional model class for deserialization
            
        Returns:
            Parsed response data
            
        Raises:
            Various GardException subclasses based on response status
        """
        response_data = None
        try:
            response_data = await response.json()
        except Exception as e:
            try:
                raw_text = await response.text()
            except Exception as inner_e:
                raw_text = f"<failed to read text: {inner_e}>"
            self.logger.error(
                "Failed to decode JSON response",
                error=str(e),
                status=response.status,
                content_type=response.headers.get("Content-Type"),
                raw_response=raw_text
            )
            raise GardException("Invalid JSON response from server")

        # Check for error responses
        if response.status >= 400:
            await self._handle_error_response(response.status, response_data)

        # Extract data from response wrapper
        if isinstance(response_data, dict) and "data" in response_data:
            data = response_data["data"]
        else:
            data = response_data

        # Convert to model if specified
        if model_class and data is not None:
            try:
                if isinstance(data, dict):
                    return model_class(**data)
                elif isinstance(data, list):
                    return [model_class(**item) for item in data]
                else:
                    return data
            except Exception as e:
                self.logger.error(
                    "Failed to create model instance",
                    model_class=model_class.__name__,
                    error=str(e)
                )
                raise GardValidationError(f"Failed to create model: {e}")

        return data

    async def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]) -> None:
        """
        Handle error responses and raise appropriate exceptions.
        
        Args:
            status_code: HTTP status code
            response_data: Response data
            
        Raises:
            Appropriate GardException subclass
        """
        error_message = response_data.get("message", "Unknown error")

        if status_code == 401:
            raise GardAuthenticationError(error_message, status_code, response_data)
        elif status_code == 404:
            raise GardNotFoundError(error_message, status_code, response_data)
        elif status_code == 429:
            raise GardRateLimitError(error_message, status_code, response_data)
        elif status_code >= 500:
            raise GardConnectionError(error_message, status_code, response_data)
        else:
            raise GardException(error_message, status_code, response_data)

    async def _make_request(
            self,
            method: str,
            endpoint: str,
            model_class: Optional[type] = None,
            **kwargs
    ) -> Any:
        """
        Make an HTTP request with automatic response handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            model_class: Optional model class for response
            **kwargs: Request parameters
            
        Returns:
            Parsed response data
        """
        url = f"{self.config.api_base_url}/{endpoint}"

        # Add JSON data if provided
        if "data" in kwargs and isinstance(kwargs["data"], dict):
            kwargs["json"] = kwargs.pop("data")

        async with self.connection_manager.request(method, url, **kwargs) as response:
            return await self._handle_response(response, model_class)

    async def get(self, endpoint: str, model_class: Optional[type] = None, **kwargs) -> Any:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, model_class, **kwargs)

    async def post(self, endpoint: str, model_class: Optional[type] = None, **kwargs) -> Any:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, model_class, **kwargs)

    async def put(self, endpoint: str, model_class: Optional[type] = None, **kwargs) -> Any:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, model_class, **kwargs)

    async def delete(self, endpoint: str, model_class: Optional[type] = None, **kwargs) -> Any:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, model_class, **kwargs)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:13
# @Description: Connection layer tests


"""
Connection layer tests for PyGard client.
"""

import asyncio
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch
from pygard.core.connection import ConnectionManager
from pygard.config import GardConfig
from pygard.utils.exceptions import GardConnectionError


class TestConnectionManager:
    """Test ConnectionManager functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GardConfig(
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def connection_manager(self, config):
        """Create connection manager instance."""
        return ConnectionManager(config)

    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self, connection_manager, config):
        """Test connection manager initialization."""
        assert connection_manager.config == config
        assert connection_manager._session is None
        assert connection_manager._connector is None

    @pytest.mark.asyncio
    async def test_start_creates_session(self, connection_manager):
        """Test that start creates a new session."""
        await connection_manager.start()

        assert connection_manager._session is not None
        assert connection_manager._connector is not None
        assert isinstance(connection_manager._session, aiohttp.ClientSession)

        # Test that subsequent calls don't create new sessions
        original_session = connection_manager._session
        await connection_manager.start()
        assert connection_manager._session is original_session

    @pytest.mark.asyncio
    async def test_close_session(self, connection_manager):
        """Test session closure."""
        await connection_manager.start()
        assert connection_manager._session is not None

        await connection_manager.close()
        assert connection_manager._session is None
        assert connection_manager._connector is None

    @pytest.mark.asyncio
    async def test_context_manager(self, connection_manager):
        """Test connection manager as context manager."""
        async with connection_manager:
            assert connection_manager._session is not None
            assert not connection_manager._session.closed

        # Session should be closed after context exit
        assert connection_manager._session is None

    @pytest.mark.asyncio
    async def test_session_property(self, connection_manager):
        """Test session property access."""
        # Should raise error when not started
        with pytest.raises(GardConnectionError):
            _ = connection_manager.session

        # Should work when started
        await connection_manager.start()
        session = connection_manager.session
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_request_success(self, connection_manager):
        """Test successful request."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            response = await connection_manager.request(
                method="GET",
                url="/test",
                params={"key": "value"}
            )

            assert response == mock_response
            mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_with_headers(self, connection_manager):
        """Test request with custom headers."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            await connection_manager.request(
                method="GET",
                url="/test",
                headers={"Authorization": "Bearer token"}
            )

            call_args = mock_session.request.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer token"

    @pytest.mark.asyncio
    async def test_request_timeout(self, connection_manager):
        """Test request timeout."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.side_effect = asyncio.TimeoutError()

        with patch.object(connection_manager, '_session', mock_session):
            with pytest.raises(GardConnectionError) as exc_info:
                await connection_manager.request(method="GET", url="/test")

            assert "Request timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_request_connection_error(self, connection_manager):
        """Test connection error handling."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.side_effect = aiohttp.ClientConnectionError("Connection failed")

        with patch.object(connection_manager, '_session', mock_session):
            with pytest.raises(GardConnectionError) as exc_info:
                await connection_manager.request(method="GET", url="/test")

            assert "Request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_request_not_started(self, connection_manager):
        """Test request when connection manager is not started."""
        with pytest.raises(GardConnectionError) as exc_info:
            await connection_manager.request(method="GET", url="/test")

        assert "Connection manager not started" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_request(self, connection_manager):
        """Test GET request method."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            result = await connection_manager.get("/test", params={"key": "value"})

            assert result == mock_response
            call_args = mock_session.request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[1]["params"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_post_request(self, connection_manager):
        """Test POST request method."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            result = await connection_manager.post("/test", json={"name": "test"})

            assert result == mock_response
            call_args = mock_session.request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[1]["json"]["name"] == "test"

    @pytest.mark.asyncio
    async def test_put_request(self, connection_manager):
        """Test PUT request method."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            result = await connection_manager.put("/test/1", json={"name": "updated"})

            assert result == mock_response
            call_args = mock_session.request.call_args
            assert call_args[0][0] == "PUT"
            assert call_args[1]["json"]["name"] == "updated"

    @pytest.mark.asyncio
    async def test_delete_request(self, connection_manager):
        """Test DELETE request method."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            result = await connection_manager.delete("/test/1")

            assert result == mock_response
            call_args = mock_session.request.call_args
            assert call_args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_request_logging(self, connection_manager):
        """Test that requests are properly logged."""
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(connection_manager, '_session', mock_session):
            with patch.object(connection_manager, 'logger') as mock_logger:
                await connection_manager.request(method="GET", url="/test")

                # Verify logger was called
                mock_logger.debug.assert_called()

    def test_default_headers(self, connection_manager):
        """Test default headers generation."""
        headers = connection_manager._get_default_headers()

        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert headers["User-Agent"] == "PyGard/0.1.0"

    def test_default_headers_with_api_key(self, config):
        """Test default headers with API key."""
        config.api_key = "test-api-key"
        connection_manager = ConnectionManager(config)

        headers = connection_manager._get_default_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-api-key"

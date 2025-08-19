#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:00
# @Description: Service layer tests

"""
Service layer tests for PyGard client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from pygard.core.base_service import BaseService
from pygard.services.gard_service import GardService
from pygard.models.entity.gard import Gard, GardFilter, GardPage
from pygard.config import GardConfig
from pygard.utils.exceptions import GardNotFoundError, GardConnectionError


class TestBaseService:
    """Test BaseService functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GardConfig(
            base_url="https://api.test.com",
            timeout=30
        )
    
    @pytest.fixture
    def mock_connection_manager(self):
        """Create mock connection manager."""
        return AsyncMock()
    
    @pytest.fixture
    def base_service(self, mock_connection_manager, config):
        """Create base service instance."""
        return BaseService(mock_connection_manager, config)
    
    @pytest.mark.asyncio
    async def test_base_service_initialization(self, base_service, mock_connection_manager, config):
        """Test base service initialization."""
        assert base_service.connection_manager == mock_connection_manager
        assert base_service.config == config
    
    @pytest.mark.asyncio
    async def test_handle_response_success(self, base_service):
        """Test successful response handling."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "test"}})
        
        result = await base_service._handle_response(mock_response, Gard)
        
        assert isinstance(result, Gard)
        assert result.name == "test"
    
    @pytest.mark.asyncio
    async def test_handle_response_without_data_wrapper(self, base_service):
        """Test response handling without data wrapper."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"name": "test"})
        
        result = await base_service._handle_response(mock_response, Gard)
        
        assert isinstance(result, Gard)
        assert result.name == "test"
    
    @pytest.mark.asyncio
    async def test_handle_response_list(self, base_service):
        """Test response handling with list data."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": [
                {"name": "test1"},
                {"name": "test2"}
            ]
        })
        
        result = await base_service._handle_response(mock_response, Gard)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, Gard) for item in result)
        assert result[0].name == "test1"
        assert result[1].name == "test2"
    
    @pytest.mark.asyncio
    async def test_handle_response_without_model(self, base_service):
        """Test response handling without model class."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "test"}})
        
        result = await base_service._handle_response(mock_response)
        
        assert result == {"name": "test"}
    
    @pytest.mark.asyncio
    async def test_handle_error_response_404(self, base_service):
        """Test handling 404 error response."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={"message": "Not found"})
        
        with pytest.raises(GardNotFoundError) as exc_info:
            await base_service._handle_response(mock_response)
        
        assert "Not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_handle_error_response_500(self, base_service):
        """Test handling 500 error response."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(return_value={"message": "Server error"})
        
        with pytest.raises(GardConnectionError) as exc_info:
            await base_service._handle_response(mock_response)
        
        assert "Server error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, base_service):
        """Test successful request making."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "test"}})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service._make_request("GET", "test", Gard)
        
        assert isinstance(result, Gard)
        assert result.name == "test"
        base_service.connection_manager.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_with_data(self, base_service):
        """Test request making with data."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "created"}})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service._make_request("POST", "test", Gard, data={"name": "test"})
        
        assert isinstance(result, Gard)
        assert result.name == "created"
        
        # Verify data was converted to json
        call_args = base_service.connection_manager.request.call_args
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "test"
    
    @pytest.mark.asyncio
    async def test_get_request(self, base_service):
        """Test GET request method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "test"}})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service.get("test", Gard, params={"key": "value"})
        
        assert isinstance(result, Gard)
        assert result.name == "test"
        
        call_args = base_service.connection_manager.request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[1]["params"]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_post_request(self, base_service):
        """Test POST request method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "created"}})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service.post("test", Gard, data={"name": "test"})
        
        assert isinstance(result, Gard)
        assert result.name == "created"
        
        call_args = base_service.connection_manager.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[1]["json"]["name"] == "test"
    
    @pytest.mark.asyncio
    async def test_put_request(self, base_service):
        """Test PUT request method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"name": "updated"}})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service.put("test/1", Gard, data={"name": "updated"})
        
        assert isinstance(result, Gard)
        assert result.name == "updated"
        
        call_args = base_service.connection_manager.request.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[1]["json"]["name"] == "updated"
    
    @pytest.mark.asyncio
    async def test_delete_request(self, base_service):
        """Test DELETE request method."""
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_response.json = AsyncMock(return_value={})
        
        base_service.connection_manager.request.return_value = mock_response
        
        result = await base_service.delete("test/1")
        
        assert result == {}
        
        call_args = base_service.connection_manager.request.call_args
        assert call_args[0][0] == "DELETE"


class TestGardService:
    """Test GardService functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GardConfig(
            base_url="https://api.test.com",
            timeout=30
        )
    
    @pytest.fixture
    def mock_connection_manager(self):
        """Create mock connection manager."""
        return AsyncMock()
    
    @pytest.fixture
    def gard_service(self, mock_connection_manager, config):
        """Create Gard service instance."""
        return GardService(mock_connection_manager, config)
    
    @pytest.fixture
    def sample_gard(self):
        """Create sample Gard instance."""
        return Gard(
            name="Test Gard",
            description="Test description",
            tags=["test", "sample"],
            type="geological"
        )
    
    @pytest.fixture
    def sample_gard_response(self):
        """Create sample Gard response data."""
        return {
            "did": 1,
            "name": "Test Gard",
            "description": "Test description",
            "tags": ["test", "sample"],
            "type": "geological",
            "create_time": "2024-01-01T00:00:00Z"
        }
    
    @pytest.mark.asyncio
    async def test_create_gard(self, gard_service, mock_connection_manager, sample_gard, sample_gard_response):
        """Test creating a Gard record."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": sample_gard_response})
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.create_gard(sample_gard)
        
        assert result.did == 1
        assert result.name == "Test Gard"
        
        # Verify request was made with correct data
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "POST"
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "Test Gard"
    
    @pytest.mark.asyncio
    async def test_update_gard(self, gard_service, mock_connection_manager, sample_gard, sample_gard_response):
        """Test updating a Gard record."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": sample_gard_response})
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.update_gard(1, sample_gard)
        
        assert result.did == 1
        assert result.name == "Test Gard"
        
        # Verify request was made with correct URL and data
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "PUT"
        assert "gard/1" in call_args[0][1]
        assert call_args[1]["json"]["name"] == "Test Gard"
    
    @pytest.mark.asyncio
    async def test_get_gard_success(self, gard_service, mock_connection_manager, sample_gard_response):
        """Test getting a Gard record successfully."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": sample_gard_response})
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.get_gard(1)
        
        assert result.did == 1
        assert result.name == "Test Gard"
        
        # Verify request was made with correct URL
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "GET"
        assert "gard/1" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_get_gard_not_found(self, gard_service, mock_connection_manager):
        """Test getting a Gard record that doesn't exist."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={"message": "Not found"})
        
        mock_connection_manager.request.return_value = mock_response
        
        with pytest.raises(GardNotFoundError) as exc_info:
            await gard_service.get_gard(999)
        
        assert "Not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_gard_success(self, gard_service, mock_connection_manager):
        """Test deleting a Gard record successfully."""
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_response.json = AsyncMock(return_value={})
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.delete_gard(1)
        
        assert result is True
        
        # Verify request was made with correct URL
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "DELETE"
        assert "gard/1" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_delete_gard_not_found(self, gard_service, mock_connection_manager):
        """Test deleting a Gard record that doesn't exist."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={"message": "Not found"})
        
        mock_connection_manager.request.return_value = mock_response
        
        with pytest.raises(GardNotFoundError):
            await gard_service.delete_gard(999)
    
    @pytest.mark.asyncio
    async def test_list_gards(self, gard_service, mock_connection_manager):
        """Test listing Gard records."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": {
                "records": [
                    {"did": 1, "name": "Gard 1", "description": "First gard"},
                    {"did": 2, "name": "Gard 2", "description": "Second gard"}
                ],
                "total": 2,
                "size": 10,
                "current": 1,
                "pages": 1
            }
        })
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.list_gards(page=1, size=10)
        
        assert isinstance(result, GardPage)
        assert result.total == 2
        assert len(result.records) == 2
        assert result.records[0].name == "Gard 1"
        assert result.records[1].name == "Gard 2"
        
        # Verify request was made with correct parameters
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "GET"
        assert "gard" in call_args[0][1]
        assert call_args[1]["params"]["page"] == 1
        assert call_args[1]["params"]["size"] == 10
    
    @pytest.mark.asyncio
    async def test_search_gards(self, gard_service, mock_connection_manager):
        """Test searching Gard records."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": {
                "records": [
                    {"did": 1, "name": "Matching Gard", "tags": ["geological"]}
                ],
                "total": 1,
                "size": 10,
                "current": 1,
                "pages": 1
            }
        })
        
        mock_connection_manager.request.return_value = mock_response
        
        filter_obj = GardFilter(tags=["geological"])
        result = await gard_service.search_gards(filter_obj, page=1, size=10)
        
        assert isinstance(result, GardPage)
        assert result.total == 1
        assert len(result.records) == 1
        assert result.records[0].name == "Matching Gard"
        
        # Verify request was made with correct data
        call_args = mock_connection_manager.request.call_args
        assert call_args[0][0] == "POST"
        assert "gard/search" in call_args[0][1]
        assert call_args[1]["json"]["tags"] == ["geological"]
        assert call_args[1]["params"]["page"] == 1
        assert call_args[1]["params"]["size"] == 10
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self, gard_service, mock_connection_manager):
        """Test searching Gard records by tags."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": {
                "records": [],
                "total": 0,
                "size": 10,
                "current": 1,
                "pages": 0
            }
        })
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.search_by_tags(["geological", "test"])
        
        assert isinstance(result, GardPage)
        assert result.total == 0
        
        # Verify that search_gards was called with correct filter
        call_args = mock_connection_manager.request.call_args
        assert "gard/search" in call_args[0][1]
        assert call_args[1]["json"]["tags"] == ["geological", "test"]
    
    @pytest.mark.asyncio
    async def test_search_by_keywords(self, gard_service, mock_connection_manager):
        """Test searching Gard records by keywords."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": {
                "records": [],
                "total": 0,
                "size": 10,
                "current": 1,
                "pages": 0
            }
        })
        
        mock_connection_manager.request.return_value = mock_response
        
        result = await gard_service.search_by_keywords(["geological", "data"])
        
        assert isinstance(result, GardPage)
        assert result.total == 0
        
        # Verify that search_gards was called with correct filter
        call_args = mock_connection_manager.request.call_args
        assert "gard/search" in call_args[0][1]
        assert call_args[1]["json"]["keywords"] == ["geological", "data"]
    
    @pytest.mark.asyncio
    async def test_get_all_gards(self, gard_service, mock_connection_manager):
        """Test getting all Gard records."""
        # Mock multiple pages
        page1_response = AsyncMock()
        page1_response.status = 200
        page1_response.json = AsyncMock(return_value={
            "data": {
                "records": [
                    {"did": 1, "name": "Gard 1"},
                    {"did": 2, "name": "Gard 2"}
                ],
                "total": 3,
                "size": 2,
                "current": 1,
                "pages": 2
            }
        })
        
        page2_response = AsyncMock()
        page2_response.status = 200
        page2_response.json = AsyncMock(return_value={
            "data": {
                "records": [
                    {"did": 3, "name": "Gard 3"}
                ],
                "total": 3,
                "size": 2,
                "current": 2,
                "pages": 2
            }
        })
        
        mock_connection_manager.request.side_effect = [page1_response, page2_response]
        
        result = await gard_service.get_all_gards()
        
        assert len(result) == 3
        assert result[0].name == "Gard 1"
        assert result[1].name == "Gard 2"
        assert result[2].name == "Gard 3"
        
        # Verify two calls were made
        assert mock_connection_manager.request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_gard_page_properties(self):
        """Test GardPage properties."""
        page = GardPage(
            records=[],
            total=10,
            size=5,
            current=2,
            pages=3
        )
        
        assert page.has_next is True
        assert page.has_previous is True
        
        # Test first page
        page.current = 1
        assert page.has_previous is False
        
        # Test last page
        page.current = 3
        assert page.has_next is False
    
    @pytest.mark.asyncio
    async def test_service_logging(self, gard_service, mock_connection_manager, sample_gard_response):
        """Test that service methods properly log operations."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": sample_gard_response})
        
        mock_connection_manager.request.return_value = mock_response
        
        with patch.object(gard_service, 'logger') as mock_logger:
            await gard_service.get_gard(1)
            
            # Verify logger was called
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, gard_service, mock_connection_manager):
        """Test error handling in service methods."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(return_value={"message": "Server error"})
        
        mock_connection_manager.request.return_value = mock_response
        
        with pytest.raises(GardConnectionError):
            await gard_service.get_gard(1)
    
    @pytest.mark.asyncio
    async def test_gard_filter_validation(self):
        """Test GardFilter validation."""
        # Valid filter
        filter_obj = GardFilter(tags=["test"], keywords=["data"])
        assert filter_obj.tags == ["test"]
        assert filter_obj.keywords == ["data"]
        
        # Empty filter
        empty_filter = GardFilter()
        assert empty_filter.tags is None
        assert empty_filter.keywords is None 
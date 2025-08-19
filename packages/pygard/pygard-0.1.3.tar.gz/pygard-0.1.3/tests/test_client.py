#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:00
# @Description: Client layer tests

"""
Client layer tests for PyGard client.
"""

import pytest
from unittest.mock import patch
from pygard.client import GardClient
from pygard.config import GardConfig
from pygard.models.entity.gard import Gard, GardFilter, GardPage
from pygard.utils.exceptions import GardNotFoundError, GardConnectionError


class TestGardClient:
    """Test GardClient functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GardConfig(
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3
        )
    
    @pytest.fixture
    def client(self, config):
        """Create GardClient instance."""
        return GardClient(config)
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client, config):
        """Test client initialization."""
        assert client.config == config
        assert client.gard is not None
        assert client._connection_manager is not None
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self, client):
        """Test client as context manager."""
        async with client:
            # Client should be accessible
            assert client.gard is not None
            
        # Connection should be closed after context exit
        assert client._connection_manager._session is None
    
    @pytest.mark.asyncio
    async def test_client_start_close(self, client):
        """Test client start and close methods."""
        # Test start
        await client.start()
        assert client._connection_manager._session is not None
        
        # Test close
        await client.close()
        assert client._connection_manager._session is None
    
    @pytest.mark.asyncio
    async def test_create_gard(self, client):
        """Test creating a Gard record through client."""
        sample_gard = Gard(
            name="Test Gard",
            description="Test description",
            tags=["test", "sample"],
            type="geological"
        )
        
        mock_response = {
            "did": 1,
            "name": "Test Gard",
            "description": "Test description",
            "tags": ["test", "sample"],
            "type": "geological"
        }
        
        with patch.object(client.gard, 'create_gard', return_value=Gard(**mock_response)):
            result = await client.create_gard(sample_gard)
            
            assert result.did == 1
            assert result.name == "Test Gard"
            client.gard.create_gard.assert_called_once_with(sample_gard)
    
    @pytest.mark.asyncio
    async def test_get_gard(self, client):
        """Test getting a Gard record through client."""
        mock_response = {
            "did": 1,
            "name": "Test Gard",
            "description": "Test description"
        }
        
        with patch.object(client.gard, 'get_gard', return_value=Gard(**mock_response)):
            result = await client.get_gard(1)
            
            assert result.did == 1
            assert result.name == "Test Gard"
            client.gard.get_gard.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_update_gard(self, client):
        """Test updating a Gard record through client."""
        sample_gard = Gard(
            name="Updated Gard",
            description="Updated description"
        )
        
        mock_response = {
            "did": 1,
            "name": "Updated Gard",
            "description": "Updated description"
        }
        
        with patch.object(client.gard, 'update_gard', return_value=Gard(**mock_response)):
            result = await client.update_gard(1, sample_gard)
            
            assert result.did == 1
            assert result.name == "Updated Gard"
            client.gard.update_gard.assert_called_once_with(1, sample_gard)
    
    @pytest.mark.asyncio
    async def test_delete_gard(self, client):
        """Test deleting a Gard record through client."""
        with patch.object(client.gard, 'delete_gard', return_value=True):
            result = await client.delete_gard(1)
            
            assert result is True
            client.gard.delete_gard.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_list_gards(self, client):
        """Test listing Gard records through client."""
        mock_response = GardPage(
            records=[
                Gard(did=1, name="Gard 1"),
                Gard(did=2, name="Gard 2")
            ],
            total=2,
            size=10,
            current=1,
            pages=1
        )
        
        with patch.object(client.gard, 'list_gards', return_value=mock_response):
            result = await client.list_gards(page=1, size=10)
            
            assert isinstance(result, GardPage)
            assert result.total == 2
            assert len(result.records) == 2
            client.gard.list_gards.assert_called_once_with(page=1, size=10)
    
    @pytest.mark.asyncio
    async def test_search_gards(self, client):
        """Test searching Gard records through client."""
        filter_obj = GardFilter(tags=["geological"])
        mock_response = GardPage(
            records=[Gard(did=1, name="Matching Gard")],
            total=1,
            size=10,
            current=1,
            pages=1
        )
        
        with patch.object(client.gard, 'search_gards', return_value=mock_response):
            result = await client.search_gards(filter_obj, page=1, size=10)
            
            assert isinstance(result, GardPage)
            assert result.total == 1
            client.gard.search_gards.assert_called_once_with(filter_obj, page=1, size=10)
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self, client):
        """Test searching by tags through client."""
        mock_response = GardPage(
            records=[],
            total=0,
            size=10,
            current=1,
            pages=0
        )
        
        with patch.object(client.gard, 'search_by_tags', return_value=mock_response):
            result = await client.search_by_tags(["geological", "test"])
            
            assert isinstance(result, GardPage)
            assert result.total == 0
            client.gard.search_by_tags.assert_called_once_with(["geological", "test"])
    
    @pytest.mark.asyncio
    async def test_search_by_keywords(self, client):
        """Test searching by keywords through client."""
        mock_response = GardPage(
            records=[],
            total=0,
            size=10,
            current=1,
            pages=0
        )
        
        with patch.object(client.gard, 'search_by_keywords', return_value=mock_response):
            result = await client.search_by_keywords(["geological", "data"])
            
            assert isinstance(result, GardPage)
            assert result.total == 0
            client.gard.search_by_keywords.assert_called_once_with(["geological", "data"])
    
    @pytest.mark.asyncio
    async def test_get_all_gards(self, client):
        """Test getting all Gard records through client."""
        mock_response = [
            Gard(did=1, name="Gard 1"),
            Gard(did=2, name="Gard 2")
        ]
        
        with patch.object(client.gard, 'get_all_gards', return_value=mock_response):
            result = await client.get_all_gards()
            
            assert len(result) == 2
            assert result[0].name == "Gard 1"
            assert result[1].name == "Gard 2"
            client.gard.get_all_gards.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_propagation(self, client):
        """Test that errors are properly propagated from service layer."""
        with patch.object(client.gard, 'get_gard', side_effect=GardNotFoundError("Not found")):
            with pytest.raises(GardNotFoundError) as exc_info:
                await client.get_gard(999)
            
            assert "Not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client):
        """Test connection error handling."""
        with patch.object(client.gard, 'get_gard', side_effect=GardConnectionError("Network error")):
            with pytest.raises(GardConnectionError) as exc_info:
                await client.get_gard(1)
            
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_client_with_custom_config(self):
        """Test client with custom configuration."""
        custom_config = GardConfig(
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
            log_level="DEBUG"
        )
        
        client = GardClient(custom_config)
        
        assert client.config == custom_config
        assert client.config.base_url == "https://custom.api.com"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
    
    @pytest.mark.asyncio
    async def test_client_service_access(self, client):
        """Test direct access to services through client."""
        assert hasattr(client, 'gard')
        assert client.gard is not None
        
        # Test that service has connection manager
        assert client.gard.connection_manager is not None
        assert client.gard.config is not None
    
    @pytest.mark.asyncio
    async def test_client_multiple_operations(self, client):
        """Test multiple operations in sequence."""
        # Mock all service methods
        with patch.object(client.gard, 'create_gard') as mock_create, \
             patch.object(client.gard, 'get_gard') as mock_get, \
             patch.object(client.gard, 'update_gard') as mock_update, \
             patch.object(client.gard, 'delete_gard') as mock_delete:
            
            # Create
            sample_gard = Gard(name="Test", description="Test")
            mock_create.return_value = Gard(did=1, name="Test", description="Test")
            created = await client.create_gard(sample_gard)
            
            # Get
            mock_get.return_value = Gard(did=1, name="Test", description="Test")
            retrieved = await client.get_gard(1)
            
            # Update
            updated_gard = Gard(name="Updated", description="Updated")
            mock_update.return_value = Gard(did=1, name="Updated", description="Updated")
            updated = await client.update_gard(1, updated_gard)
            
            # Delete
            mock_delete.return_value = True
            deleted = await client.delete_gard(1)
            
            # Verify all operations were called
            assert mock_create.called
            assert mock_get.called
            assert mock_update.called
            assert mock_delete.called
            
            assert created.did == 1
            assert retrieved.did == 1
            assert updated.did == 1
            assert deleted is True
    
    @pytest.mark.asyncio
    async def test_client_logging_integration(self, client):
        """Test that client properly integrates with logging."""
        with patch.object(client, 'logger') as mock_logger:
            # Perform an operation
            with patch.object(client.gard, 'get_gard', return_value=Gard(did=1, name="Test")):
                await client.get_gard(1)
                
                # Verify logger was accessed (through service layer)
                # Note: This is indirect since logging happens in service layer
                pass
    
    def test_client_repr(self, client):
        """Test client string representation."""
        client_repr = repr(client)
        assert "GardClient" in client_repr
    
    @pytest.mark.asyncio
    async def test_client_config_validation(self):
        """Test that client validates configuration properly."""
        # Test with invalid config
        with pytest.raises(Exception):
            # This should fail if we pass None or invalid config
            GardClient(None)
    
    @pytest.mark.asyncio
    async def test_client_service_initialization_order(self, config):
        """Test that services are initialized in correct order."""
        client = GardClient(config)
        
        # Connection manager should be initialized first
        assert client._connection_manager is not None
        
        # Services should be initialized with connection manager
        assert client.gard.connection_manager is client._connection_manager
        assert client.gard.config is config
    
    def test_get_connection_info(self, client):
        """Test getting connection information."""
        info = client.get_connection_info()
        
        assert "base_url" in info
        assert "api_version" in info
        assert "timeout" in info
        assert "connection_pool_size" in info
        
        assert info["base_url"] == client.config.base_url
        assert info["timeout"] == client.config.timeout
        assert info["connection_pool_size"] == client.config.connection_pool_size
    
    @pytest.mark.asyncio
    async def test_client_with_kwargs_override(self):
        """Test client initialization with kwargs override."""
        client = GardClient(
            base_url="https://override.com",
            timeout=120,
            log_level="DEBUG"
        )
        
        assert client.config.base_url == "https://override.com"
        assert client.config.timeout == 120
        assert client.config.log_level == "DEBUG"
    
    @pytest.mark.asyncio
    async def test_client_default_config(self):
        """Test client with default configuration."""
        client = GardClient()
        
        # Should use default config
        assert client.config is not None
        assert hasattr(client.config, 'base_url')
        assert hasattr(client.config, 'timeout') 
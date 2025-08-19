#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:00
# @Description: Integration tests

"""
Integration tests for PyGard client.
"""

import pytest
import asyncio
from unittest.mock import patch
from datetime import datetime
from pygard import GardClient
from pygard.config import GardConfig
from pygard.models.entity.gard import Gard, GardFilter, GardPage
from pygard.utils.exceptions import GardNotFoundError, GardConnectionError


class TestPyGardIntegration:
    """Integration tests for PyGard framework."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GardConfig(
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
            log_level="INFO"
        )
    
    @pytest.fixture
    def client(self, config):
        """Create GardClient instance."""
        return GardClient(config)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test complete workflow: create, read, update, delete."""
        # Mock responses for the workflow
        create_response = {
            "did": 1,
            "name": "Test Gard",
            "description": "Test description",
            "tags": ["test", "sample"],
            "type": "geological",
            "create_time": "2024-01-01T00:00:00Z"
        }
        
        update_response = {
            "did": 1,
            "name": "Updated Gard",
            "description": "Updated description",
            "tags": ["test", "sample", "updated"],
            "type": "geological",
            "update_time": "2024-01-01T01:00:00Z"
        }
        
        # Mock service methods
        with patch.object(client.gard, 'create_gard', return_value=Gard(**create_response)), \
             patch.object(client.gard, 'get_gard', return_value=Gard(**create_response)), \
             patch.object(client.gard, 'update_gard', return_value=Gard(**update_response)), \
             patch.object(client.gard, 'delete_gard', return_value=True):
            
            # 1. Create Gard
            sample_gard = Gard(
                name="Test Gard",
                description="Test description",
                tags=["test", "sample"],
                type="geological"
            )
            
            created = await client.create_gard(sample_gard)
            assert created.did == 1
            assert created.name == "Test Gard"
            
            # 2. Get Gard
            retrieved = await client.get_gard(1)
            assert retrieved.did == 1
            assert retrieved.name == "Test Gard"
            
            # 3. Update Gard
            updated_gard = Gard(
                name="Updated Gard",
                description="Updated description",
                tags=["test", "sample", "updated"]
            )
            
            updated = await client.update_gard(1, updated_gard)
            assert updated.did == 1
            assert updated.name == "Updated Gard"
            assert "updated" in updated.tags
            
            # 4. Delete Gard
            deleted = await client.delete_gard(1)
            assert deleted is True
    
    @pytest.mark.asyncio
    async def test_search_and_pagination_workflow(self, client):
        """Test search and pagination workflow."""
        # Mock paginated responses
        page1_response = GardPage(
            records=[
                Gard(did=1, name="Gard 1", tags=["geological"]),
                Gard(did=2, name="Gard 2", tags=["geological"])
            ],
            total=3,
            size=2,
            current=1,
            pages=2
        )
        
        page2_response = GardPage(
            records=[
                Gard(did=3, name="Gard 3", tags=["geological"])
            ],
            total=3,
            size=2,
            current=2,
            pages=2
        )
        
        with patch.object(client.gard, 'list_gards', side_effect=[page1_response, page2_response]):
            # Test pagination
            page1 = await client.list_gards(page=1, size=2)
            assert page1.total == 3
            assert len(page1.records) == 2
            assert page1.has_next is True
            assert page1.has_previous is False
            
            page2 = await client.list_gards(page=2, size=2)
            assert page2.total == 3
            assert len(page2.records) == 1
            assert page2.has_next is False
            assert page2.has_previous is True
    
    @pytest.mark.asyncio
    async def test_search_workflow(self, client):
        """Test search workflow."""
        search_response = GardPage(
            records=[
                Gard(did=1, name="Geological Data", tags=["geological", "test"]),
                Gard(did=2, name="Another Geological", tags=["geological", "sample"])
            ],
            total=2,
            size=10,
            current=1,
            pages=1
        )
        
        with patch.object(client.gard, 'search_gards', return_value=search_response):
            # Test search by filter
            filter_obj = GardFilter(tags=["geological"], keywords=["data"])
            results = await client.search_gards(filter_obj)
            
            assert results.total == 2
            assert len(results.records) == 2
            assert all("geological" in gard.tags for gard in results.records)
            
            # Test search by tags
            tag_results = await client.search_by_tags(["geological"])
            assert tag_results.total == 2
            
            # Test search by keywords
            keyword_results = await client.search_by_keywords(["data"])
            assert keyword_results.total == 2
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, client):
        """Test error handling throughout the workflow."""
        # Test GardNotFoundError
        with patch.object(client.gard, 'get_gard', side_effect=GardNotFoundError("Not found")):
            with pytest.raises(GardNotFoundError) as exc_info:
                await client.get_gard(999)
            assert "Not found" in str(exc_info.value)
        
        # Test GardConnectionError
        with patch.object(client.gard, 'create_gard', side_effect=GardConnectionError("Network error")):
            with pytest.raises(GardConnectionError) as exc_info:
                sample_gard = Gard(name="Test", description="Test")
                await client.create_gard(sample_gard)
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_configuration_integration(self):
        """Test configuration integration across all layers."""
        # Test with different configurations
        configs = [
            GardConfig(base_url="https://api1.test.com", timeout=30),
            GardConfig(base_url="https://api2.test.com", timeout=60, max_retries=5),
            GardConfig(base_url="https://api3.test.com", log_level="DEBUG")
        ]
        
        for config in configs:
            client = GardClient(config)
            
            # Verify configuration is properly propagated
            assert client.config == config
            assert client._connection_manager.config == config
            assert client.gard.config == config
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self, client):
        """Test connection lifecycle management."""
        # Test automatic connection management
        async with client:
            # Client should be connected
            assert client._connection_manager._session is not None
            
            # Perform operations
            with patch.object(client.gard, 'get_gard', return_value=Gard(did=1, name="Test")):
                result = await client.get_gard(1)
                assert result.did == 1
        
        # Connection should be closed after context exit
        assert client._connection_manager._session is None
    
    @pytest.mark.asyncio
    async def test_model_serialization_integration(self, client):
        """Test model serialization integration."""
        # Create Gard with datetime fields
        gard = Gard(
            name="Test Gard",
            description="Test description",
            create_time=datetime(2024, 1, 1, 12, 0, 0),
            update_time=datetime(2024, 1, 1, 13, 0, 0)
        )
        
        # Test to_dict (excludes None values)
        dict_data = gard.to_dict()
        assert "name" in dict_data
        assert "description" in dict_data
        assert "create_time" in dict_data
        assert "update_time" in dict_data
        
        # Test to_api_dict (includes datetime serialization)
        api_data = gard.to_api_dict()
        assert "name" in api_data
        assert "description" in api_data
        assert "create_time" in api_data
        assert "update_time" in api_data
        
        # Verify datetime serialization
        assert isinstance(api_data["create_time"], str)
        assert isinstance(api_data["update_time"], str)
        assert api_data["create_time"] == "2024-01-01T12:00:00"
        assert api_data["update_time"] == "2024-01-01T13:00:00"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, client):
        """Test concurrent operations."""
        # Mock responses for concurrent operations
        responses = [
            Gard(did=1, name="Gard 1"),
            Gard(did=2, name="Gard 2"),
            Gard(did=3, name="Gard 3")
        ]
        
        with patch.object(client.gard, 'get_gard', side_effect=responses):
            # Perform concurrent operations
            tasks = [
                client.get_gard(1),
                client.get_gard(2),
                client.get_gard(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert results[0].did == 1
            assert results[1].did == 2
            assert results[2].did == 3
    
    @pytest.mark.asyncio
    async def test_data_validation_integration(self, client):
        """Test data validation integration."""
        # Test valid data
        valid_gard = Gard(
            name="Valid Gard",
            description="Valid description",
            tags=["valid", "test"],
            type="geological"
        )
        
        # This should not raise any validation errors
        assert valid_gard.name == "Valid Gard"
        assert valid_gard.tags == ["valid", "test"]
        
        # Test invalid data (should raise validation errors)
        with pytest.raises(Exception):
            # Missing required field 'name'
            invalid_gard = Gard(description="Only description")
    
    @pytest.mark.asyncio
    async def test_framework_extensibility(self, client):
        """Test framework extensibility."""
        # Test that the framework can be extended with new services
        # This would typically involve creating new service classes
        # For now, we test that the existing service structure is extensible
        
        # Verify service structure
        assert hasattr(client, 'gard')
        assert hasattr(client.gard, 'connection_manager')
        assert hasattr(client.gard, 'config')
        
        # Verify that new services could be added following the same pattern
        # This is a structural test rather than functional
        assert isinstance(client.gard.connection_manager, type(client._connection_manager))
        assert isinstance(client.gard.config, type(client.config))
    
    @pytest.mark.asyncio
    async def test_client_with_kwargs_override(self):
        """Test client with kwargs override."""
        client = GardClient(
            base_url="https://override.com",
            timeout=120,
            log_level="DEBUG"
        )
        
        assert client.config.base_url == "https://override.com"
        assert client.config.timeout == 120
        assert client.config.log_level == "DEBUG"
    
    @pytest.mark.asyncio
    async def test_connection_info_integration(self, client):
        """Test connection info integration."""
        info = client.get_connection_info()
        
        assert "base_url" in info
        assert "api_version" in info
        assert "timeout" in info
        assert "connection_pool_size" in info
        
        assert info["base_url"] == client.config.base_url
        assert info["timeout"] == client.config.timeout 
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:07
# @Description:


"""
Main client class for PyGard.
"""

from typing import Optional, Any

from ..config import GardConfig
from ..core import setup_logger, ConnectionManager
from ..services import GardService, SheetService, GeometryService
from ..models import (
    Gard, GardFilter, GardPage, Sheet,
    SheetRegisterRequest, SheetLoadRequest, SheetQueryRequest,
    SheetRegisterResponse, SheetLoadResponse, QueryData, Geometry, GeometryRegisterResponse, GeometryRegisterRequest,
    GeometryLoadRequest, GeometryLoadResponse, GeometryQueryRequest
)


class GardClient:
    """
    Main client for interacting with the Gard data service.
    
    This client provides a high-level interface for all Gard operations,
    including connection management, logging, and service access.
    """

    def __init__(
            self,
            config: Optional[GardConfig] = None,
            **kwargs
    ) -> None:
        """
        Initialize Gard client.
        
        Args:
            config: Gard configuration (optional)
            **kwargs: Configuration overrides
        """
        # Initialize configuration
        if config is None:
            config = GardConfig()

        # Apply any overrides
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.config = config

        # Setup logging
        self.logger = setup_logger(
            level=config.log_level,
            format_type=config.log_format
        )

        # Initialize connection manager
        self._connection_manager = ConnectionManager(config)

        # Initialize services
        self._gard_service = GardService(self._connection_manager, config)
        self._sheet_service = SheetService(self._connection_manager, config)
        self._geometry_service = GeometryService(self._connection_manager, config)

        self.logger.info(
            "Gard client initialized",
            base_url=config.base_url,
            api_version=config.api_version
        )

    async def __aenter__(self) -> "GardClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the client and establish connections."""
        await self._connection_manager.start()
        self.logger.info("Gard client started")

    async def close(self) -> None:
        """Close the client and clean up resources."""
        await self._connection_manager.close()
        self.logger.info("Gard client closed")

    @property
    def gard(self) -> GardService:
        """Get the Gard service."""
        return self._gard_service

    @property
    def sheet(self) -> SheetService:
        """Get the Sheet service."""
        return self._sheet_service

    @property
    def geometry(self) -> GeometryService:
        """Get the Geometry service."""
        return self._geometry_service

    def get_connection_info(self) -> dict:
        """Get connection information."""
        return {
            "base_url": self.config.base_url,
            "api_version": self.config.api_version,
            "timeout": self.config.timeout,
            "connection_pool_size": self.config.connection_pool_size,
        }

    ##################################################
    ### Convenience methods for common operations
    ##################################################

    async def create_gard(self, gard: Gard) -> Gard:
        """Create a new Gard record."""
        return await self.gard.create_gard(gard)

    async def get_gard(self, did: int) -> Gard:
        """Get a Gard record by ID."""
        return await self.gard.get_gard(did)

    async def update_gard(self, did: int, gard: Gard) -> Gard:
        """Update a Gard record."""
        return await self.gard.update_gard(did, gard)

    async def delete_gard(self, did: int) -> bool:
        """Delete a Gard record."""
        return await self.gard.delete_gard(did)

    async def list_gards(self, page: int = 1, size: int = 10) -> GardPage:
        """List Gard records with pagination."""
        return await self.gard.list_gards(page, size)

    async def search_gards(
            self,
            filter_obj: GardFilter,
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records with filters."""
        return await self.gard.search_gards(filter_obj, page, size)

    async def search_by_tags(
            self,
            tags: list[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records by tags."""
        return await self.gard.search_by_tags(tags, page, size)

    async def search_by_keywords(
            self,
            keywords: list[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records by keywords."""
        return await self.gard.search_by_keywords(keywords, page, size)

    async def get_all_gards(self) -> list[Gard]:
        """Get all Gard records."""
        return await self.gard.get_all_gards()

    ##################################################
    ### Sheet convenience methods
    ##################################################

    # async def create_sheet(self, sheet: Sheet) -> Sheet:
    #     """Create a new Sheet record."""
    #     return await self.sheet.create_sheet(sheet)

    async def get_sheet(self, id: int) -> Sheet:
        """Get a Sheet record by ID."""
        return await self.sheet.get_sheet(id)

    async def update_sheet(self, id: int, sheet: Sheet) -> Sheet:
        """Update a Sheet record."""
        return await self.sheet.update_sheet(id, sheet)

    async def delete_sheet(self, id: int) -> bool:
        """Delete a Sheet record."""
        return await self.sheet.delete_sheet(id)

    # async def list_sheets(self, page: int = 1, size: int = 10) -> list[Sheet]:
    #     """List Sheet records with pagination."""
    #     return await self.sheet.list_sheets(page, size)

    async def register_sheet(self, request: SheetRegisterRequest) -> SheetRegisterResponse:
        """Register a new Sheet record."""
        return await self.sheet.register_sheet(request)

    async def load_sheet(self, request: SheetLoadRequest) -> SheetLoadResponse:
        """Load a Sheet record."""
        return await self.sheet.load_sheet(request)

    async def query_sheet(self, request: SheetQueryRequest) -> QueryData:
        """Query Sheet records."""
        return await self.sheet.query_sheet(request)

    ##################################################
    ### Geometry convenience methods
    ##################################################

    async def get_geometry(self, id: str) -> Geometry:
        """Get a Geometry record by ID."""
        return await self.geometry.get_geometry(id)

    async def update_geometry(self, id: str, geometry: Geometry) -> Geometry:
        """Update a Geometry record."""
        return await self.geometry.update_geometry(id, geometry)

    async def delete_geometry(self, id: str) -> bool:
        """Delete a Geometry record."""
        return await self.geometry.delete_geometry(id)

    async def register_geometry(self, request: GeometryRegisterRequest) -> GeometryRegisterResponse:
        """Register a new Geometry record."""
        return await self.geometry.register_geometry(request)

    async def load_geometry(self, request: GeometryLoadRequest) -> GeometryLoadResponse:
        """Load a Geometry record."""
        return await self.geometry.load_geometry(request)

    async def query_geometry(self, request: GeometryQueryRequest) -> QueryData:
        """Query Geometry records."""
        return await self.geometry.query_geometry(request)

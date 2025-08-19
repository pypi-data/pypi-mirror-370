# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:59
# @Description:


"""
Gard service for PyGard client.
"""

import structlog
from typing import List

from ..core import BaseService
from ..models import Gard, GardFilter, GardPage
from ..utils import GardNotFoundError


class GardService(BaseService[Gard]):
    """Service for Gard data operations."""

    def __init__(self, connection_manager, config):
        """Initialize Gard service."""
        super().__init__(connection_manager, config)
        self.logger = structlog.get_logger(__name__)

    async def create_gard(self, gard: Gard) -> Gard:
        """
        Create a new Gard record.
        
        Args:
            gard: Gard data to create
            
        Returns:
            Created Gard record
        """
        self.logger.info("Creating Gard record", name=gard.name)

        data = gard.to_api_dict()
        result = await self.post("gard", Gard, data=data)

        self.logger.info("Gard record created", did=result.did)
        return result

    async def update_gard(self, did: int, gard: Gard) -> Gard:
        """
        Update an existing Gard record.
        
        Args:
            did: Data ID
            gard: Updated Gard data
            
        Returns:
            Updated Gard record
            
        Raises:
            GardNotFoundError: If Gard record not found
        """
        self.logger.info("Updating Gard record", did=did)

        data = gard.to_api_dict()
        result = await self.put(f"gard/{did}", Gard, data=data)

        self.logger.info("Gard record updated", did=did)
        return result

    async def get_gard(self, did: int) -> Gard:
        """
        Get a Gard record by ID.
        
        Args:
            did: Data ID
            
        Returns:
            Gard record
            
        Raises:
            GardNotFoundError: If Gard record not found
        """
        self.logger.info("Getting Gard record", did=did)

        result = await self.get(f"gard/{did}", Gard)

        if not result:
            raise GardNotFoundError(f"Gard record with ID {did} not found")

        self.logger.info("Gard record retrieved", did=did)
        return result

    async def delete_gard(self, did: int) -> bool:
        """
        Delete a Gard record.
        
        Args:
            did: Data ID
            
        Returns:
            Deleted Gard record ID
            
        Raises:
            GardNotFoundError: If Gard record not found
        """
        self.logger.info("Deleting Gard record", did=did)

        try:
            result = await self.delete(f"gard/{did}")
            self.logger.info("Gard record deleted", did=did)
            return result
        except GardNotFoundError:
            self.logger.warning("Gard record not found for deletion", did=did)
            raise

    async def list_gards(
            self,
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """
        List Gard records with pagination.
        
        Args:
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Paginated Gard results
        """
        self.logger.info("Listing Gard records", page=page, size=size)

        params = {"page": page, "size": size}
        result = await self.get("gard", GardPage, params=params)

        self.logger.info(
            "Gard records listed",
            total=result.total,
            current_page=result.current,
            total_pages=result.pages
        )
        return result

    async def search_gards(
            self,
            filter_obj: GardFilter,
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """
        Search Gard records with filters.
        
        Args:
            filter_obj: Search filters
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Paginated Gard results
        """
        self.logger.info(
            "Searching Gard records",
            filter=filter_obj.model_dump(),
            page=page,
            size=size
        )

        params = {"page": page, "size": size}
        data = filter_obj.model_dump()
        result = await self.post("gard/search", GardPage, params=params, data=data)

        self.logger.info(
            "Gard records searched",
            total=result.total,
            current_page=result.current,
            total_pages=result.pages
        )
        return result

    async def search_by_tags(
            self,
            tags: List[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """
        Search Gard records by tags.
        
        Args:
            tags: List of tags to search for
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Paginated Gard results
        """
        filter_obj = GardFilter(tags=tags)
        return await self.search_gards(filter_obj, page, size)

    async def search_by_keywords(
            self,
            keywords: List[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """
        Search Gard records by keywords.
        
        Args:
            keywords: List of keywords to search for
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Paginated Gard results
        """
        filter_obj = GardFilter(keywords=keywords)
        return await self.search_gards(filter_obj, page, size)

    async def get_all_gards(self) -> List[Gard]:
        """
        Get all Gard records (without pagination).
        
        Returns:
            List of all Gard records
        """
        self.logger.info("Getting all Gard records")

        all_gards = []
        page = 1

        while True:
            result = await self.list_gards(page=page, size=100)
            all_gards.extend(result.records)

            if not result.has_next:
                break

            page += 1

        self.logger.info("All Gard records retrieved", total=len(all_gards))
        return all_gards

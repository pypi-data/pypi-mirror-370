# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/7/1 19:06
# @Description:


import structlog
from typing import List, Any

from ..core import BaseService
from ..models import (
    Geometry, GeometryRegisterRequest, GeometryLoadRequest, GeometryQueryRequest,
    GeometryRegisterResponse, GeometryLoadResponse, QueryData
)


class GeometryService(BaseService[Geometry]):
    """Service for Geometry data operations."""

    def __init__(self, connection_manager, config):
        super().__init__(connection_manager, config)
        self.logger = structlog.get_logger(__name__)

    # async def create_geometry(self, geometry: Geometry) -> Geometry:
    #     self.logger.info("Creating Geometry record", name=geometry.name)
    #     data = geometry.to_api_dict()
    #     result = await self.post("geometry", Geometry, data=data)
    #     self.logger.info("Geometry record created", id=result.id)
    #     return result

    async def update_geometry(self, id: str, geometry: Geometry) -> Geometry:
        self.logger.info("Updating Geometry record", id=id)
        data = geometry.to_api_dict()
        result = await self.put(f"geometry/{id}", Geometry, data=data)
        self.logger.info("Geometry record updated", id=id)
        return result

    async def get_geometry(self, id: str) -> Geometry:
        self.logger.info("Getting Geometry record", id=id)
        result = await self.get(f"geometry/{id}", Geometry)
        if not result:
            raise RuntimeError(f"Geometry record with ID {id} not found")
        self.logger.info("Geometry record retrieved", id=id)
        return result

    async def delete_geometry(self, id: str) -> bool:
        self.logger.info("Deleting Geometry record", id=id)
        result = await self.delete(f"geometry/{id}")
        self.logger.info("Geometry record deleted", id=id)
        return result

    # async def list_geometries(self, page: int = 1, size: int = 10) -> List[Geometry]:
    #     self.logger.info("Listing Geometry records", page=page, size=size)
    #     params = {"page": page, "size": size}
    #     result = await self.get("geometry", None, params=params)
    #     self.logger.info("Geometry records listed", count=len(result.get('records', [])))
    #     return [Geometry.from_dict(item) for item in result.get('records', [])]

    async def register_geometry(self, request: GeometryRegisterRequest) -> GeometryRegisterResponse:
        self.logger.info("Registering Geometry")
        data = request.to_api_dict()
        result = await self.post("geometry/register", GeometryRegisterResponse, data=data)
        self.logger.info("Geometry registered")
        return result

    async def load_geometry(self, request: GeometryLoadRequest) -> GeometryLoadResponse:
        self.logger.info("Loading Geometry")
        data = request.to_api_dict()
        result = await self.post("geometry/load", GeometryLoadResponse, data=data)
        self.logger.info("Geometry loaded")
        return result

    async def query_geometry(self, request: GeometryQueryRequest) -> QueryData:
        self.logger.info("Querying Geometry")
        data = request.to_api_dict()
        result = await self.post("geometry/query", QueryData, data=data)
        self.logger.info("Geometry query executed")
        return result

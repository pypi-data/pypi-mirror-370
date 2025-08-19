# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/30 15:14
# @Description:


import structlog
from typing import List, Any

from ..core import BaseService
from ..models import (
    Sheet,
    SheetQueryRequest, SheetRegisterRequest, SheetLoadRequest,
    SheetRegisterResponse, SheetLoadResponse, QueryData
)


class SheetService(BaseService[Sheet]):
    """Service for Sheet data operations."""

    def __init__(self, connection_manager, config):
        super().__init__(connection_manager, config)
        self.logger = structlog.get_logger(__name__)

    # async def create_sheet(self, sheet: Sheet) -> Sheet:
    #     self.logger.info("Creating Sheet record", name=sheet.name)
    #     data = sheet.to_api_dict()
    #     result = await self.post("sheet", Sheet, data=data)
    #     self.logger.info("Sheet record created", id=result.id)
    #     return result

    async def update_sheet(self, id: int, sheet: Sheet) -> Sheet:
        self.logger.info("Updating Sheet record", id=id)
        data = sheet.to_api_dict()
        result = await self.put(f"sheet/{id}", Sheet, data=data)
        self.logger.info("Sheet record updated", id=id)
        return result

    async def get_sheet(self, id: int) -> Sheet:
        self.logger.info("Getting Sheet record", id=id)
        result = await self.get(f"sheet/{id}", Sheet)
        if not result:
            raise RuntimeError(f"Sheet record with ID {id} not found")
        self.logger.info("Sheet record retrieved", id=id)
        return result

    async def delete_sheet(self, id: int) -> bool:
        self.logger.info("Deleting Sheet record", id=id)
        result = await self.delete(f"sheet/{id}")
        self.logger.info("Sheet record deleted", id=id)
        return result

    # async def list_sheets(self, page: int = 1, size: int = 10) -> List[Sheet]:
    #     self.logger.info("Listing Sheet records", page=page, size=size)
    #     params = {"page": page, "size": size}
    #     result = await self.get("sheet", None, params=params)
    #     self.logger.info("Sheet records listed", count=len(result.get('records', [])))
    #     return [Sheet.from_dict(item) for item in result.get('records', [])]

    async def register_sheet(self, request: SheetRegisterRequest) -> SheetRegisterResponse:
        """
        Register a new Sheet record.

        Args:
            request: Sheet register data

        Returns:
            Registered Sheet record
        """
        self.logger.info("Registering Sheet record", name=request.sheet.name, load=request.load)
        data = request.to_api_dict()
        result = await self.post("sheet/register", SheetRegisterResponse, data=data)
        self.logger.info("Sheet record registered", id=result.sheet.id)
        return result

    async def load_sheet(self, request: SheetLoadRequest) -> SheetLoadResponse:
        self.logger.info("Loading Sheet record", id=request.sheet.id, name=request.sheet.name)
        data = request.to_api_dict()
        result = await self.post("sheet/load", SheetLoadResponse, data=data)
        self.logger.info("Sheet record loaded", id=result.sheet_id, name=result.sheet_name)
        return result

    async def query_sheet(self, request: SheetQueryRequest) -> QueryData:
        self.logger.info("Querying Sheet record", id=request.sheet.id)
        data = request.to_api_dict()
        result = await self.post("sheet/query", QueryData, data=data)
        self.logger.info("Sheet record queried", id=request.sheet.id)
        return result

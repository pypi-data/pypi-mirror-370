# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/30 17:13
# @Description:


from typing import Optional
from pydantic import BaseModel, Field

from ..models import Geometry, Gard, Sheet


class SheetRegisterRequest(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    sheet: Sheet = Field(None, description="Sheet information")
    load: bool = Field(False, description="Load data into the sheet or not")

    def to_api_dict(self) -> dict:
        """Convert to API dictionary format."""
        data = self.model_dump(exclude_none=True)
        if self.gard:
            data['gard'] = self.gard.to_api_dict()
        if self.sheet:
            data['sheet'] = self.sheet.to_api_dict()
        return data


class SheetLoadRequest(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    sheet: Sheet = Field(None, description="Sheet information")

    def to_api_dict(self) -> dict:
        data = self.model_dump(exclude_none=True)
        if self.gard:
            data['gard'] = self.gard.to_api_dict()
        if self.sheet:
            data['sheet'] = self.sheet.to_api_dict()
        return data


class SheetQueryRequest(BaseModel):
    sheet: Sheet = Field(None, description="Sheet information")
    sql: Optional[str] = Field(None, description="SQL query to execute on the sheet")
    page: Optional[int] = Field(1, description="Page number for pagination")
    size: Optional[int] = Field(20, description="Page size for pagination")

    def to_api_dict(self) -> dict:
        data = self.model_dump(exclude_none=True)
        if self.sheet:
            data['sheet'] = self.sheet.to_api_dict()
        return data


class GeometryRegisterRequest(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    geometry: Geometry = Field(None, description="Geometry information")
    load: bool = Field(False, description="Load data into the geometry or not")

    def to_api_dict(self) -> dict:
        """Convert to API dictionary format."""
        data = self.model_dump(exclude_none=True)
        if self.gard:
            data['gard'] = self.gard.to_api_dict()
        if self.geometry:
            data['geometry'] = self.geometry.to_api_dict()
        return data


class GeometryLoadRequest(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    geometry: Geometry = Field(None, description="Geometry information")

    def to_api_dict(self) -> dict:
        """Convert to API dictionary format."""
        data = self.model_dump(exclude_none=True)
        if self.gard:
            data['gard'] = self.gard.to_api_dict()
        if self.geometry:
            data['geometry'] = self.geometry.to_api_dict()
        return data


class GeometryQueryRequest(BaseModel):
    geometry: Geometry = Field(None, description="Geometry information")
    sql: Optional[str] = Field(None, description="SQL query to execute on the geometry")
    page: Optional[int] = Field(1, description="Page number for pagination")
    size: Optional[int] = Field(20, description="Page size for pagination")

    def to_api_dict(self) -> dict:
        """Convert to API dictionary format."""
        data = self.model_dump(exclude_none=True)
        if self.geometry:
            data['geometry'] = self.geometry.to_api_dict()
        return data

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/30 17:13
# @Description:


from typing import Optional, Any
from pydantic import BaseModel, Field

from pygard.models import Geometry
from pygard.models.entity.gard import Gard
from pygard.models.entity.sheet import Sheet


class SheetRegisterResponse(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    sheet: Sheet = Field(None, description="Sheet information")


class SheetLoadResponse(BaseModel):
    sheet_id: Optional[str] = Field(None, description="Sheet ID")
    sheet_name: Optional[str] = Field(None, description="Sheet name")


class GeometryRegisterResponse(BaseModel):
    gard: Gard = Field(None, description="Gard information")
    geometry: Optional[Geometry] = Field(None, description="Geometry information")


class GeometryLoadResponse(BaseModel):
    geometry_id: Optional[str] = Field(None, description="Geometry ID")
    geometry_name: Optional[str] = Field(None, description="Geometry name")


class QueryData(BaseModel):
    total: int = Field(None, description="Total number of records")
    data: Optional[list] = Field(None, description="Data list")
    size: Optional[int] = Field(None, description="Total size of records")
    page: Optional[int] = Field(None, description="Current page number")

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/7/1 19:07
# @Description:


from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pygard.models.common import Column


class Geometry(BaseModel):
    id: Optional[str] = Field(None, description="Geometry ID")
    name: Optional[str] = Field(None, description="Geometry Name")
    table_name: Optional[str] = Field(None, description="Table Name")
    description: Optional[str] = Field(None, description="Description")
    oss_file_path: Optional[str] = Field(None, description="OSS File Path")
    crs: Optional[str] = Field(None, description="CRS")
    column_list: Optional[list[Column]] = Field(None, description="List of Columns")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    def to_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def to_api_dict(self) -> dict:
        data = self.model_dump(exclude_none=True)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Geometry":
        return cls(**data)

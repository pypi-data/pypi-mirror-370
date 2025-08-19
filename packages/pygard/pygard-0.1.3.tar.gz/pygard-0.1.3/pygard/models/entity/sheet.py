# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/30 15:17
# @Description:

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from pygard.models.common import Column


class Sheet(BaseModel):
    """Sheet data model."""
    id: Optional[str] = Field(None, description="Sheet ID")
    name: str = Field(None, description="Sheet name")
    table_name: str = Field(None, description="Table name")
    description: Optional[str] = Field(None, description="Description")
    oss_file_path: Optional[str] = Field(None, description="OSS file path")
    column_list: Optional[List[Column]] = Field(None, description="List of columns")
    # create_time: Optional[datetime] = Field(None, description="Creation time")
    # update_time: Optional[datetime] = Field(None, description="Update time")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    def to_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def to_api_dict(self) -> dict:
        data = self.model_dump(exclude_none=True)
        # if self.create_time:
        #     data['create_time'] = self.create_time.isoformat()
        # if self.update_time:
        #     data['update_time'] = self.update_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Sheet":
        return cls(**data)

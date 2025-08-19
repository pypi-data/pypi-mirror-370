# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:00
# @Description:


"""
Gard data models for PyGard client.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from pygard.models.common import Bbox2D, VerticalRange, Other, RevisionHistory


class GardTypeEnum(str, Enum):
    TABLE = "TABLE"
    GEOMETRY = "GEOMETRY"
    RASTER = "RASTER"
    OTHER = "Other"


class Gard(BaseModel):
    """Gard data model."""

    # Core fields
    did: Optional[int] = Field(None, description="Data ID")
    name: str = Field(None, description="Name of the data")
    description: Optional[str] = Field(None, description="Description")
    tags: Optional[List[str]] = Field(None, description="Tags")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    version: Optional[str] = Field(None, description="Version")
    status: Optional[str] = Field(None, description="Status")
    access: Optional[str] = Field(None, description="Access level")
    create_time: Optional[datetime] = Field(None, description="Creation time")
    update_time: Optional[datetime] = Field(None, description="Update time")

    # Type information
    type: GardTypeEnum = Field(GardTypeEnum.OTHER, description="Type of the Gard data")
    is_spatial: Optional[bool] = Field(None, description="Is spatial data")
    is_temporal: Optional[bool] = Field(None, description="Is temporal data")

    # Other metadata
    other: Optional[Other] = Field(None, description="Other metadata")

    # Spatial information
    coordinate_system: Optional[str] = Field(None, description="Coordinate system")
    spatial_representation: Optional[str] = Field(None, description="Spatial representation")
    geometry_type: Optional[str] = Field(None, description="Geometry type")
    bbox: Optional[Bbox2D] = Field(None, description="Bounding box")
    vertical_range: Optional[VerticalRange] = Field(None, description="Vertical range")
    spatial_resolution: Optional[float] = Field(None, description="Spatial resolution")

    # Temporal information
    temporal_type: Optional[str] = Field(None, description="Temporal type")
    gts_type: Optional[str] = Field(None, description="GTS type")
    is_paleo: Optional[bool] = Field(None, description="Is paleo data")
    is_circa: Optional[bool] = Field(None, description="Is circa data")
    temporal_resolution: Optional[str] = Field(None, description="Temporal resolution")
    start_time: Optional[str] = Field(None, description="Start time")
    end_time: Optional[str] = Field(None, description="End time")
    geologic_start_time: Optional[str] = Field(None, description="Geologic start time")
    geologic_end_time: Optional[str] = Field(None, description="Geologic end time")
    isotope_start_time: Optional[str] = Field(None, description="Isotope start time")
    isotope_end_time: Optional[str] = Field(None, description="Isotope end time")

    # Source information
    provider: Optional[str] = Field(None, description="Data provider")
    source_description: Optional[str] = Field(None, description="Source description")
    reference: Optional[str] = Field(None, description="Reference")
    license: Optional[str] = Field(None, description="License")
    external_link: Optional[str] = Field(None, description="External link")
    total_size: Optional[int] = Field(None, description="Total size in bytes")

    # Quality information
    reliability_score: Optional[float] = Field(None, description="Reliability score")
    revision_history: Optional[List[RevisionHistory]] = Field(None, description="Revision history")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def to_api_dict(self) -> dict:
        """Convert to dictionary for API requests, with datetime serialization."""
        data = self.model_dump(exclude_none=True)

        # Handle datetime serialization
        if self.create_time:
            data['create_time'] = self.create_time.isoformat()
        if self.update_time:
            data['update_time'] = self.update_time.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Gard":
        """Create Gard instance from dictionary."""
        return cls(**data)


class GardFilter(BaseModel):
    """Filter model for Gard search."""

    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    keywords: Optional[List[str]] = Field(None, description="Filter by keywords")


class GardPage(BaseModel):
    """Paginated Gard results."""

    records: List["Gard"] = Field(..., description="List of Gard records")
    total: int = Field(..., description="Total number of records")
    size: int = Field(..., description="Page size")
    current: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.current < self.pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.current > 1

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:59
# @Description:


"""
Tests for PyGard models.
"""

from pygard.models import Gard, GardFilter, GardPage, Bbox2D, VerticalRange, Other


class TestGardModel:
    """Test Gard model."""

    def test_gard_creation(self):
        """Test creating a Gard instance."""
        gard = Gard(
            name="Test Data",
            description="Test description",
            tags=["test", "sample"],
            type="GEOMETRY"
        )

        assert gard.name == "Test Data"
        assert gard.description == "Test description"
        assert gard.tags == ["test", "sample"]
        assert gard.type == "GEOMETRY"
        assert gard.did is None

    def test_gard_to_dict(self):
        """Test converting Gard to dictionary."""
        gard = Gard(
            name="Test Data",
            description="Test description",
            tags=["test"]
        )

        data = gard.to_dict()
        assert "name" in data
        assert "description" in data
        assert "tags" in data
        assert "did" not in data  # None values should be excluded

    def test_gard_from_dict(self):
        """Test creating Gard from dictionary."""
        data = {
            "name": "Test Data",
            "description": "Test description",
            "tags": ["test"],
            "type": "GEOMETRY"
        }

        gard = Gard.from_dict(data)
        assert gard.name == "Test Data"
        assert gard.description == "Test description"
        assert gard.tags == ["test"]
        assert gard.type == "GEOMETRY"


class TestGardFilterModel:
    """Test GardFilter model."""

    def test_filter_creation(self):
        """Test creating a GardFilter instance."""
        filter_obj = GardFilter(
            tags=["geology", "paleontology"],
            keywords=["fossil", "strata"]
        )

        assert filter_obj.tags == ["geology", "paleontology"]
        assert filter_obj.keywords == ["fossil", "strata"]

    def test_filter_empty(self):
        """Test creating an empty GardFilter."""
        filter_obj = GardFilter()
        assert filter_obj.tags is None
        assert filter_obj.keywords is None


class TestGardPageModel:
    """Test GardPage model."""

    def test_page_creation(self):
        """Test creating a GardPage instance."""
        gards = [
            Gard(name="Data 1"),
            Gard(name="Data 2")
        ]

        page = GardPage(
            records=gards,
            total=100,
            size=10,
            current=1,
            pages=10
        )

        assert len(page.records) == 2
        assert page.total == 100
        assert page.size == 10
        assert page.current == 1
        assert page.pages == 10

    def test_page_pagination_properties(self):
        """Test pagination properties."""
        gards = [Gard(name="Data")]
        page = GardPage(
            records=gards,
            total=50,
            size=10,
            current=1,
            pages=5
        )

        assert page.has_next is True
        assert page.has_previous is False

        # Test last page
        last_page = GardPage(
            records=gards,
            total=50,
            size=10,
            current=5,
            pages=5
        )

        assert last_page.has_next is False
        assert last_page.has_previous is True


class TestCommonModels:
    """Test common models."""

    def test_bbox2d_creation(self):
        """Test creating a Bbox2D instance."""
        bbox = Bbox2D(
            min_x=0.0,
            min_y=0.0,
            max_x=100.0,
            max_y=100.0
        )

        assert bbox.min_x == 0.0
        assert bbox.min_y == 0.0
        assert bbox.max_x == 100.0
        assert bbox.max_y == 100.0

    def test_vertical_range_creation(self):
        """Test creating a VerticalRange instance."""
        vr = VerticalRange(
            min_z=0.0,
            max_z=1000.0,
            unit="meters"
        )

        assert vr.min_z == 0.0
        assert vr.max_z == 1000.0
        assert vr.unit == "meters"

    def test_other_model_dict_access(self):
        """Test Other model dictionary-like access."""
        other = Other()
        other["key1"] = "value1"
        other["key2"] = 42

        assert other["key1"] == "value1"
        assert other["key2"] == 42
        assert other.get("key1") == "value1"
        assert other.get("nonexistent", "default") == "default"
        assert list(other.keys()) == ["key1", "key2"]
        assert list(other.values()) == ["value1", 42]

"""
Tests for JSON Schema Helper Component

Author: Eli Newman
Date: February 2026
"""

import pytest
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from json_schema import (
    create_entity_json,
    validate_entity_json,
    json_to_string,
    string_to_json,
    merge_entities
)


class TestCreateEntityJson:
    """Test suite for create_entity_json function."""

    def test_create_minimal(self):
        """Test creating JSON with minimal data."""
        result = create_entity_json()

        assert result['pmid'] is None
        assert result['title'] is None
        assert result['abstract'] is None
        assert result['entities']['diseases'] == []
        assert result['entities']['genes'] == []
        assert result['entities']['drugs'] == []
        assert result['entities']['symptoms'] == []

    def test_create_with_metadata(self):
        """Test creating JSON with metadata fields."""
        result = create_entity_json(
            pmid="12345",
            title="Test Title",
            abstract="Test Abstract"
        )

        assert result['pmid'] == "12345"
        assert result['title'] == "Test Title"
        assert result['abstract'] == "Test Abstract"

    def test_create_with_entities(self):
        """Test creating JSON with entity lists."""
        result = create_entity_json(
            diseases=["cancer", "carcinoma"],
            genes=["TP53", "KRAS"],
            drugs=["fluorouracil"],
            symptoms=["pain", "bleeding"]
        )

        assert len(result['entities']['diseases']) == 2
        assert len(result['entities']['genes']) == 2
        assert len(result['entities']['drugs']) == 1
        assert len(result['entities']['symptoms']) == 2

    def test_create_complete(self):
        """Test creating complete JSON with all fields."""
        result = create_entity_json(
            pmid="12345",
            title="Cancer Study",
            abstract="A study about cancer.",
            diseases=["cancer"],
            genes=["TP53"],
            drugs=["drug1"],
            symptoms=["symptom1"]
        )

        assert result['pmid'] == "12345"
        assert len(result['entities']['diseases']) == 1
        assert len(result['entities']['genes']) == 1

    def test_empty_lists_default(self):
        """Test that None values default to empty lists for entities."""
        result = create_entity_json(
            pmid="12345",
            diseases=None  # Explicitly None
        )

        assert result['entities']['diseases'] == []


class TestValidateEntityJson:
    """Test suite for validate_entity_json function."""

    def test_validate_correct_schema(self):
        """Test validation of correctly formatted JSON."""
        data = create_entity_json(pmid="12345")
        valid, errors = validate_entity_json(data)

        assert valid is True
        assert len(errors) == 0

    def test_validate_missing_pmid(self):
        """Test detection of missing pmid field."""
        data = {
            "title": "Test",
            "abstract": "Test",
            "entities": {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "symptoms": []
            }
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("pmid" in err for err in errors)

    def test_validate_missing_entities(self):
        """Test detection of missing entities field."""
        data = {
            "pmid": "12345",
            "title": "Test",
            "abstract": "Test"
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("entities" in err for err in errors)

    def test_validate_missing_entity_type(self):
        """Test detection of missing entity type."""
        data = {
            "pmid": "12345",
            "title": "Test",
            "abstract": "Test",
            "entities": {
                "diseases": [],
                "genes": [],
                "drugs": []
                # Missing symptoms
            }
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("symptoms" in err for err in errors)

    def test_validate_wrong_entity_type(self):
        """Test detection of wrong type for entity list."""
        data = {
            "pmid": "12345",
            "title": "Test",
            "abstract": "Test",
            "entities": {
                "diseases": "not a list",  # Should be list
                "genes": [],
                "drugs": [],
                "symptoms": []
            }
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("diseases" in err and "list" in err for err in errors)

    def test_validate_extra_entity_keys(self):
        """Test detection of extra keys in entities."""
        data = {
            "pmid": "12345",
            "title": "Test",
            "abstract": "Test",
            "entities": {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "symptoms": [],
                "extra_field": []  # Not in schema
            }
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("extra" in err.lower() for err in errors)

    def test_validate_entities_not_dict(self):
        """Test detection of non-dict entities field."""
        data = {
            "pmid": "12345",
            "title": "Test",
            "abstract": "Test",
            "entities": []  # Should be dict, not list
        }
        valid, errors = validate_entity_json(data)

        assert valid is False
        assert any("dict" in err for err in errors)


class TestJsonConversion:
    """Test suite for JSON string conversion functions."""

    def test_json_to_string_pretty(self):
        """Test pretty JSON string conversion."""
        data = create_entity_json(pmid="12345")
        json_str = json_to_string(data, pretty=True)

        assert isinstance(json_str, str)
        assert '\n' in json_str  # Pretty format has newlines
        assert '"pmid"' in json_str

    def test_json_to_string_compact(self):
        """Test compact JSON string conversion."""
        data = create_entity_json(pmid="12345")
        json_str = json_to_string(data, pretty=False)

        assert isinstance(json_str, str)
        # Compact format should be shorter
        assert len(json_str) < len(json_to_string(data, pretty=True))

    def test_string_to_json(self):
        """Test parsing JSON string."""
        data = create_entity_json(pmid="12345", title="Test")
        json_str = json_to_string(data)
        parsed = string_to_json(json_str)

        assert parsed['pmid'] == "12345"
        assert parsed['title'] == "Test"

    def test_string_to_json_invalid(self):
        """Test that invalid JSON raises error."""
        invalid_json = "{ not valid json }"

        with pytest.raises(json.JSONDecodeError):
            string_to_json(invalid_json)

    def test_roundtrip_conversion(self):
        """Test that conversion is reversible."""
        original = create_entity_json(
            pmid="12345",
            title="Test",
            diseases=["cancer", "carcinoma"]
        )

        # Convert to string and back
        json_str = json_to_string(original)
        result = string_to_json(json_str)

        assert result == original


class TestMergeEntities:
    """Test suite for merge_entities function."""

    def test_merge_basic(self):
        """Test basic merging of two JSON objects."""
        json1 = create_entity_json(
            pmid="12345",
            title="Test",
            diseases=["cancer"]
        )
        json2 = create_entity_json(
            diseases=["carcinoma"]
        )

        merged = merge_entities(json1, json2)

        assert merged['pmid'] == "12345"  # From json1
        assert len(merged['entities']['diseases']) == 2
        assert "cancer" in merged['entities']['diseases']
        assert "carcinoma" in merged['entities']['diseases']

    def test_merge_removes_duplicates(self):
        """Test that merging removes duplicate entities (case-insensitive)."""
        json1 = create_entity_json(diseases=["cancer", "Cancer"])
        json2 = create_entity_json(diseases=["CANCER", "carcinoma"])

        merged = merge_entities(json1, json2)

        # Should only have 2 unique: cancer (some capitalization) and carcinoma
        assert len(merged['entities']['diseases']) == 2

    def test_merge_multiple_entity_types(self):
        """Test merging with multiple entity types."""
        json1 = create_entity_json(
            diseases=["cancer"],
            genes=["TP53"]
        )
        json2 = create_entity_json(
            diseases=["carcinoma"],
            drugs=["fluorouracil"]
        )

        merged = merge_entities(json1, json2)

        assert len(merged['entities']['diseases']) == 2
        assert len(merged['entities']['genes']) == 1
        assert len(merged['entities']['drugs']) == 1

    def test_merge_preserves_metadata(self):
        """Test that metadata from json1 is preserved."""
        json1 = create_entity_json(
            pmid="12345",
            title="Title1",
            abstract="Abstract1"
        )
        json2 = create_entity_json(
            pmid="99999",  # Different PMID
            title="Title2"
        )

        merged = merge_entities(json1, json2)

        # Should keep json1's metadata
        assert merged['pmid'] == "12345"
        assert merged['title'] == "Title1"
        assert merged['abstract'] == "Abstract1"


class TestEdgeCases:
    """Test suite for edge cases and special scenarios."""

    def test_unicode_in_entities(self):
        """Test handling of Unicode characters in entity names."""
        result = create_entity_json(
            diseases=["β-thalassemia", "α-synuclein"]
        )

        assert len(result['entities']['diseases']) == 2

    def test_very_long_entity_lists(self):
        """Test handling of large entity lists."""
        diseases = [f"disease{i}" for i in range(1000)]
        result = create_entity_json(diseases=diseases)

        assert len(result['entities']['diseases']) == 1000

    def test_empty_string_entities(self):
        """Test handling of empty string in entity list."""
        result = create_entity_json(diseases=["cancer", "", "carcinoma"])

        assert len(result['entities']['diseases']) == 3
        assert "" in result['entities']['diseases']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

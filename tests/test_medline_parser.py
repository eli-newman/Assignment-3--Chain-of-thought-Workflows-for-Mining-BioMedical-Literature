"""
Tests for MEDLINE Parser Component

Author: Eli Newman
Date: February 2026
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from medline_parser import parse_medline_record


class TestMedlineParser:
    """Test suite for MEDLINE parsing functionality."""

    def test_simple_record(self):
        """Test parsing a simple, complete MEDLINE record."""
        record = """PMID- 12345
TI  - This is a test title
AB  - This is a test abstract.
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert result['title'] == 'This is a test title'
        assert result['abstract'] == 'This is a test abstract.'

    def test_multiline_title(self):
        """Test parsing a title that spans multiple lines."""
        record = """PMID- 12345
TI  - This is a very long title that spans
      multiple lines and should be concatenated
      properly.
AB  - Short abstract.
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert 'multiple lines' in result['title']
        assert 'properly' in result['title']
        # Check that continuation is joined with spaces
        assert result['title'] == 'This is a very long title that spans multiple lines and should be concatenated properly.'

    def test_multiline_abstract(self):
        """Test parsing an abstract that spans multiple lines."""
        record = """PMID- 12345
TI  - Test Title
AB  - This is a test abstract that spans
      multiple lines. It should be handled
      correctly by the parser.
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert 'multiple lines' in result['abstract']
        assert 'correctly' in result['abstract']

    def test_missing_title(self):
        """Test handling of record without title."""
        record = """PMID- 12345
AB  - Abstract only.
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert result['title'] is None
        assert result['abstract'] == 'Abstract only.'

    def test_missing_abstract(self):
        """Test handling of record without abstract."""
        record = """PMID- 12345
TI  - Title only
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert result['title'] == 'Title only'
        assert result['abstract'] is None

    def test_missing_all_fields(self):
        """Test handling of record with no relevant fields."""
        record = """AU  - Smith J
SO  - Journal Name
"""
        result = parse_medline_record(record)

        assert result['pmid'] is None
        assert result['title'] is None
        assert result['abstract'] is None

    def test_empty_input(self):
        """Test handling of empty input."""
        result = parse_medline_record("")

        assert result['pmid'] is None
        assert result['title'] is None
        assert result['abstract'] is None

    def test_real_medline_format(self):
        """Test with a real MEDLINE record format."""
        record = """PMID- 41631282
OWN - NLM
STAT- PubMed-not-MEDLINE
TI  - Novel Utilization of Circulating Tumor DNA in Primary Dedifferentiated Seminal
      Vesicle Adenocarcinoma: A Case Report.
PG  - 62-69
AB  - Primary seminal vesicle adenocarcinoma (PSVA) is an exceptionally rare
      malignancy, with fewer than 100 cases reported worldwide. This case
      highlights the importance of comprehensive imaging.
FAU - Malshy, Kamil
AU  - Malshy K
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '41631282'
        assert 'Circulating Tumor DNA' in result['title']
        assert 'exceptionally rare' in result['abstract']
        assert 'comprehensive imaging' in result['abstract']

    def test_special_characters(self):
        """Test handling of special characters in text."""
        record = """PMID- 12345
TI  - Title with special chars: α, β, γ-radiation
AB  - Abstract with quotes "test" and apostrophe's.
"""
        result = parse_medline_record(record)

        assert 'α' in result['title'] or 'α' in result['title']  # Handle encoding
        assert 'quotes' in result['abstract']

    def test_very_long_abstract(self):
        """Test handling of very long abstract."""
        long_abstract_lines = ["AB  - " + "Word " * 50]
        for _ in range(10):
            long_abstract_lines.append("      " + "Word " * 50)

        record = "PMID- 12345\nTI  - Test\n" + "\n".join(long_abstract_lines)
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert result['abstract'] is not None
        assert len(result['abstract']) > 100  # Should be long

    def test_pmid_with_different_format(self):
        """Test PMID extraction with various whitespace."""
        # PMID- format (standard)
        record1 = "PMID- 12345\n"
        assert parse_medline_record(record1)['pmid'] == '12345'

        # PMID  format (with spaces)
        record2 = "PMID  12345\n"
        assert parse_medline_record(record2)['pmid'] == '12345'

    def test_fields_in_different_order(self):
        """Test that field order doesn't matter."""
        record = """AB  - Abstract first
PMID- 12345
TI  - Title last
"""
        result = parse_medline_record(record)

        assert result['pmid'] == '12345'
        assert result['title'] == 'Title last'
        assert result['abstract'] == 'Abstract first'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

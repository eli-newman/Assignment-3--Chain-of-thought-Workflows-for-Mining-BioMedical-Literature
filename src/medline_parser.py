"""
MEDLINE Parser Component

This module provides functionality to parse MEDLINE formatted records
and extract PMID, title, and abstract fields.

Author: Eli Newman
Date: February 2026
"""

import re
from typing import Dict, Optional


def parse_medline_record(medline_text: str) -> Dict[str, Optional[str]]:
    """
    Parse a MEDLINE record and extract PMID, title, and abstract.

    MEDLINE format uses tags like:
    - PMID- : PubMed ID
    - TI  - : Title
    - AB  - : Abstract

    Continuation lines are indented with spaces.

    Args:
        medline_text: Raw MEDLINE formatted text

    Returns:
        Dictionary with keys: 'pmid', 'title', 'abstract'
        Values are strings or None if field not found

    Example:
        >>> record = "PMID- 12345\\nTI  - Test Title\\nAB  - Test Abstract"
        >>> parse_medline_record(record)
        {'pmid': '12345', 'title': 'Test Title', 'abstract': 'Test Abstract'}
    """
    result = {
        'pmid': None,
        'title': None,
        'abstract': None
    }

    if not medline_text or not medline_text.strip():
        return result

    lines = medline_text.split('\n')
    current_field = None
    current_content = []

    for line in lines:
        # Check if this is a new field (tag line)
        # Tags are 2-4 chars followed by dash or spaces
        tag_match = re.match(r'^([A-Z]{2,4})[\s\-]+(.*)$', line)

        if tag_match:
            # Save previous field if any
            if current_field and current_content:
                content = ' '.join(current_content).strip()
                if current_field == 'PMID':
                    result['pmid'] = content
                elif current_field == 'TI':
                    result['title'] = content
                elif current_field == 'AB':
                    result['abstract'] = content

            # Start new field
            tag = tag_match.group(1)
            content = tag_match.group(2).strip()

            if tag in ['PMID', 'TI', 'AB']:
                current_field = tag
                current_content = [content] if content else []
            else:
                current_field = None
                current_content = []

        elif current_field and line.strip():
            # This is a continuation line (indented)
            # Add to current field content
            current_content.append(line.strip())

    # Don't forget the last field
    if current_field and current_content:
        content = ' '.join(current_content).strip()
        if current_field == 'PMID':
            result['pmid'] = content
        elif current_field == 'TI':
            result['title'] = content
        elif current_field == 'AB':
            result['abstract'] = content

    return result


def parse_medline_file(file_path: str) -> list[Dict[str, Optional[str]]]:
    """
    Parse a file containing multiple MEDLINE records.

    Records are separated by blank lines.

    Args:
        file_path: Path to MEDLINE file

    Returns:
        List of parsed record dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on double newlines to separate records
    # But MEDLINE records are actually continuous, so this is simplified
    # In practice, we need better logic to detect record boundaries
    records = []
    current_record = []

    for line in content.split('\n'):
        if line.startswith('PMID-') and current_record:
            # New record starting, save previous
            record_text = '\n'.join(current_record)
            parsed = parse_medline_record(record_text)
            if parsed['pmid']:  # Only add if we found a PMID
                records.append(parsed)
            current_record = [line]
        else:
            current_record.append(line)

    # Don't forget the last record
    if current_record:
        record_text = '\n'.join(current_record)
        parsed = parse_medline_record(record_text)
        if parsed['pmid']:
            records.append(parsed)

    return records


if __name__ == '__main__':
    # Simple test
    sample = """PMID- 41631282
TI  - Novel Utilization of Circulating Tumor DNA in Primary Dedifferentiated Seminal
      Vesicle Adenocarcinoma: A Case Report.
AB  - Primary seminal vesicle adenocarcinoma (PSVA) is an exceptionally rare
      malignancy. This case highlights the importance of comprehensive imaging.
"""

    result = parse_medline_record(sample)
    print("Parsed result:")
    print(f"PMID: {result['pmid']}")
    print(f"Title: {result['title']}")
    print(f"Abstract: {result['abstract'][:100]}..." if result['abstract'] else "No abstract")

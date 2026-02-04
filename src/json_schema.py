"""
JSON Schema Helper Component

This module provides functionality to construct and validate JSON objects
for biomedical entity extraction following a fixed schema.

Author: Eli Newman
Date: February 2026
"""

from typing import Dict, List, Optional, Any
import json


def create_entity_json(
    pmid: Optional[str] = None,
    title: Optional[str] = None,
    abstract: Optional[str] = None,
    diseases: Optional[List[str]] = None,
    genes: Optional[List[str]] = None,
    drugs: Optional[List[str]] = None,
    symptoms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Construct a JSON object following the biomedical entity schema.

    Schema:
    {
      "pmid": "string",
      "title": "string",
      "abstract": "string",
      "entities": {
        "diseases": [],
        "genes": [],
        "drugs": [],
        "symptoms": []
      }
    }

    Args:
        pmid: PubMed ID
        title: Article title
        abstract: Article abstract
        diseases: List of disease names
        genes: List of gene names
        drugs: List of drug names
        symptoms: List of symptom names

    Returns:
        Dictionary following the entity schema

    Example:
        >>> result = create_entity_json(
        ...     pmid="12345",
        ...     title="Cancer Study",
        ...     diseases=["cancer", "carcinoma"]
        ... )
        >>> result['pmid']
        '12345'
        >>> len(result['entities']['diseases'])
        2
    """
    return {
        "pmid": pmid,
        "title": title,
        "abstract": abstract,
        "entities": {
            "diseases": diseases if diseases is not None else [],
            "genes": genes if genes is not None else [],
            "drugs": drugs if drugs is not None else [],
            "symptoms": symptoms if symptoms is not None else []
        }
    }


def validate_entity_json(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate that a dictionary follows the required entity schema.

    Checks:
    - All required keys present
    - Entity lists are lists (not other types)
    - No extra keys in entities object

    Args:
        data: Dictionary to validate

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> good_data = create_entity_json(pmid="123")
        >>> validate_entity_json(good_data)
        (True, [])
        >>> bad_data = {"pmid": "123"}  # missing fields
        >>> valid, errors = validate_entity_json(bad_data)
        >>> valid
        False
    """
    errors = []

    # Check top-level keys
    required_keys = ["pmid", "title", "abstract", "entities"]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    # Check entities structure
    if "entities" in data:
        if not isinstance(data["entities"], dict):
            errors.append("'entities' must be a dictionary")
        else:
            entity_types = ["diseases", "genes", "drugs", "symptoms"]
            for entity_type in entity_types:
                if entity_type not in data["entities"]:
                    errors.append(f"Missing entity type: {entity_type}")
                elif not isinstance(data["entities"][entity_type], list):
                    errors.append(f"'{entity_type}' must be a list")

            # Check for extra keys
            extra_keys = set(data["entities"].keys()) - set(entity_types)
            if extra_keys:
                errors.append(f"Extra keys in entities: {extra_keys}")

    return (len(errors) == 0, errors)


def json_to_string(data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Convert entity JSON to string format.

    Args:
        data: Entity dictionary
        pretty: If True, format with indentation

    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)


def string_to_json(json_str: str) -> Dict[str, Any]:
    """
    Parse JSON string to entity dictionary.

    Args:
        json_str: JSON formatted string

    Returns:
        Entity dictionary

    Raises:
        json.JSONDecodeError: If string is not valid JSON
    """
    return json.loads(json_str)


def merge_entities(json1: Dict[str, Any], json2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two entity JSON objects.

    Keeps pmid, title, abstract from json1.
    Combines entity lists from both (removing duplicates).

    Args:
        json1: First entity dictionary
        json2: Second entity dictionary

    Returns:
        Merged entity dictionary
    """
    merged = create_entity_json(
        pmid=json1.get("pmid"),
        title=json1.get("title"),
        abstract=json1.get("abstract")
    )

    # Merge entity lists
    entity_types = ["diseases", "genes", "drugs", "symptoms"]
    for entity_type in entity_types:
        entities1 = json1.get("entities", {}).get(entity_type, [])
        entities2 = json2.get("entities", {}).get(entity_type, [])

        # Combine and deduplicate (preserving order)
        seen = set()
        combined = []
        for entity in entities1 + entities2:
            if entity.lower() not in seen:
                seen.add(entity.lower())
                combined.append(entity)

        merged["entities"][entity_type] = combined

    return merged


if __name__ == '__main__':
    # Simple test
    result = create_entity_json(
        pmid="12345",
        title="Test Article",
        abstract="This is a test abstract about cancer.",
        diseases=["cancer", "carcinoma"],
        genes=["TP53"],
        drugs=["fluorouracil"],
        symptoms=["pain"]
    )

    print("Created JSON:")
    print(json_to_string(result))

    valid, errors = validate_entity_json(result)
    print(f"\nValidation: {valid}")
    if errors:
        print(f"Errors: {errors}")

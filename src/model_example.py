"""
Example Model Call Component

This module demonstrates how to:
1. Build a prompt
2. Call a model (mocked in this example)
3. Parse the JSON output
4. Feed it into the JSON schema helper

Author: Eli Newman
Date: February 2026
"""

import json
from medline_parser import parse_medline_record
from json_schema import create_entity_json, validate_entity_json, json_to_string


# Load prompts from documentation
ENTITY_EXTRACTION_PROMPT_TEMPLATE = """You are a biomedical entity extraction specialist. Analyze the following medical text and identify all relevant biomedical entities.

Extract the following entity types:
1. DISEASES: Any disease, condition, or pathology mentioned
2. GENES: Gene names and symbols
3. DRUGS: Medications, therapeutic agents, or compounds
4. SYMPTOMS: Clinical manifestations or symptoms

Text to analyze:
{text}

Return ONLY a JSON object with this structure:
{{
  "diseases": [],
  "genes": [],
  "drugs": [],
  "symptoms": []
}}
"""


def build_prompt(title: str, abstract: str) -> str:
    """
    Build a prompt for entity extraction.

    Args:
        title: Article title
        abstract: Article abstract

    Returns:
        Formatted prompt string
    """
    text = f"Title: {title}\n\nAbstract: {abstract}"
    return ENTITY_EXTRACTION_PROMPT_TEMPLATE.format(text=text)


def call_model_mock(prompt: str) -> str:
    """
    Mock model call - simulates calling Gemma/Phi/Qwen.

    In a real implementation, this would call an actual LLM API.
    For this example, we return a mock response.

    Args:
        prompt: The prompt to send to the model

    Returns:
        Model response (JSON string)
    """
    # This is a MOCK response - in reality, you would call:
    # - Ollama API for local models
    # - OpenAI API for GPT models
    # - Anthropic API for Claude
    # etc.

    # Simulated response based on the sample MEDLINE record
    mock_response = {
        "diseases": [
            "seminal vesicle adenocarcinoma",
            "carcinoma",
            "malignancy",
            "prostate adenocarcinoma",
            "dedifferentiated carcinoma"
        ],
        "genes": [],
        "drugs": [],
        "symptoms": [
            "lower urinary tract symptoms"
        ]
    }

    return json.dumps(mock_response, indent=2)


def parse_model_response(response: str) -> dict:
    """
    Parse model response from JSON string.

    Args:
        response: JSON string from model

    Returns:
        Dictionary with entities

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing model response: {e}")
        print(f"Response was: {response}")
        # Return empty entities on parse error
        return {
            "diseases": [],
            "genes": [],
            "drugs": [],
            "symptoms": []
        }


def extract_entities_from_record(medline_text: str) -> dict:
    """
    Complete pipeline: parse MEDLINE -> extract entities -> create JSON.

    Args:
        medline_text: Raw MEDLINE record

    Returns:
        Complete entity JSON following schema
    """
    # Step 1: Parse MEDLINE record
    print("Step 1: Parsing MEDLINE record...")
    parsed = parse_medline_record(medline_text)
    print(f"  Found PMID: {parsed['pmid']}")
    print(f"  Title length: {len(parsed['title']) if parsed['title'] else 0} chars")
    print(f"  Abstract length: {len(parsed['abstract']) if parsed['abstract'] else 0} chars")

    # Step 2: Build prompt
    print("\nStep 2: Building prompt for model...")
    if parsed['title'] and parsed['abstract']:
        prompt = build_prompt(parsed['title'], parsed['abstract'])
        print(f"  Prompt length: {len(prompt)} chars")
    else:
        print("  ERROR: Missing title or abstract, cannot build prompt")
        return create_entity_json(
            pmid=parsed['pmid'],
            title=parsed['title'],
            abstract=parsed['abstract']
        )

    # Step 3: Call model (mocked)
    print("\nStep 3: Calling model (MOCKED)...")
    response = call_model_mock(prompt)
    print("  Model response received")

    # Step 4: Parse response
    print("\nStep 4: Parsing model response...")
    entities = parse_model_response(response)
    print(f"  Extracted {len(entities.get('diseases', []))} diseases")
    print(f"  Extracted {len(entities.get('genes', []))} genes")
    print(f"  Extracted {len(entities.get('drugs', []))} drugs")
    print(f"  Extracted {len(entities.get('symptoms', []))} symptoms")

    # Step 5: Create final JSON
    print("\nStep 5: Creating final JSON...")
    final_json = create_entity_json(
        pmid=parsed['pmid'],
        title=parsed['title'],
        abstract=parsed['abstract'],
        diseases=entities.get('diseases', []),
        genes=entities.get('genes', []),
        drugs=entities.get('drugs', []),
        symptoms=entities.get('symptoms', [])
    )

    # Step 6: Validate
    print("\nStep 6: Validating JSON schema...")
    valid, errors = validate_entity_json(final_json)
    if valid:
        print("  ✓ JSON is valid")
    else:
        print(f"  ✗ Validation errors: {errors}")

    return final_json


def main():
    """Run example with sample MEDLINE record."""
    # Sample MEDLINE record (shortened for demo)
    sample_record = """PMID- 41631282
TI  - Novel Utilization of Circulating Tumor DNA in Primary Dedifferentiated Seminal
      Vesicle Adenocarcinoma: A Case Report of Molecular Clearance Following Multimodal
      Therapy.
AB  - Primary seminal vesicle adenocarcinoma (PSVA) is an exceptionally rare
      malignancy, with fewer than 100 cases reported worldwide and poses significant
      diagnostic and surveillance challenges due to its deep pelvic location,
      nonspecific clinical manifestations, frequent coexistence with other
      genitourinary malignancies, and lack of validated serum tumor markers. A
      77-year-old male with long-standing lower urinary tract symptoms and mildly
      elevated prostate-specific antigen was found to have a large (7.4 cm)
      predominantly cystic pelvic mass replacing the left seminal vesicle on magnetic
      resonance imaging. Histologic evaluation revealed synchronous high-grade prostate
      adenocarcinoma and a distinct dedifferentiated carcinoma not arising from
      prostatic tissue.
"""

    print("=" * 70)
    print("MEDLINE ENTITY EXTRACTION EXAMPLE")
    print("=" * 70)

    result = extract_entities_from_record(sample_record)

    print("\n" + "=" * 70)
    print("FINAL RESULT:")
    print("=" * 70)
    print(json_to_string(result))

    print("\n" + "=" * 70)
    print("NOTE: This example uses a MOCK model response.")
    print("In a real implementation, you would:")
    print("  1. Install ollama: https://ollama.ai/")
    print("  2. Pull a model: ollama pull gemma")
    print("  3. Call API: requests.post('http://localhost:11434/api/generate', ...)")
    print("=" * 70)


if __name__ == '__main__':
    main()

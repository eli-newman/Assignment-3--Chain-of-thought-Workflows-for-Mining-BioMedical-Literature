"""
Process MEDLINE Records with Real Ollama LLM

This script uses actual LLM models (Gemma/Phi/Qwen) via Ollama
to extract biomedical entities from MEDLINE records.

Author: Eli Newman
Date: February 2026
"""

import json
import os
import requests
from datetime import datetime
from medline_parser import parse_medline_file
from json_schema import create_entity_json, json_to_string, validate_entity_json


# Prompt template from our documentation
ENTITY_EXTRACTION_PROMPT = """You are a biomedical entity extraction specialist. Analyze the following medical text and identify all relevant biomedical entities.

Extract the following entity types:
1. DISEASES: Any disease, condition, or pathology mentioned (e.g., cancer, carcinoma, adenocarcinoma, malignancy)
2. GENES: Gene names and symbols (e.g., TP53, KRAS, BRCA1)
3. DRUGS: Medications, therapeutic agents, or compounds (e.g., fluorouracil, bevacizumab, oxaliplatin)
4. SYMPTOMS: Clinical manifestations or symptoms (e.g., pain, bleeding, obstruction)

Text to analyze:
Title: {title}

Abstract: {abstract}

Instructions:
- Extract exact phrases as they appear in the text
- Include multi-word entities (e.g., "rectal cancer" not just "cancer")
- Do not include general medical terms unless they are specific conditions
- If an entity appears multiple times, list it only once

Return ONLY a JSON object with this structure (no additional text):
{{
  "diseases": [],
  "genes": [],
  "drugs": [],
  "symptoms": []
}}"""


def call_ollama(prompt: str, model: str = "phi3:mini") -> str:
    """
    Call Ollama API to generate a response.

    Args:
        prompt: The prompt to send to the model
        model: Model name (e.g., "phi3:mini", "gemma", "qwen")

    Returns:
        Model response as string

    Raises:
        requests.exceptions.RequestException: If API call fails
    """
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low temperature for more deterministic output
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        raise


def extract_json_from_response(response: str) -> dict:
    """
    Extract JSON from LLM response.

    The model might return extra text, so we need to extract just the JSON.

    Args:
        response: Raw response from LLM

    Returns:
        Parsed JSON dictionary
    """
    # Try to find JSON in the response
    response = response.strip()

    # Look for JSON object boundaries
    start = response.find('{')
    end = response.rfind('}')

    if start != -1 and end != -1:
        json_str = response[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Attempted to parse: {json_str[:200]}...")
            # Return empty entities on parse error
            return {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "symptoms": []
            }

    # No JSON found
    print("No JSON found in response")
    print(f"Response was: {response[:200]}...")
    return {
        "diseases": [],
        "genes": [],
        "drugs": [],
        "symptoms": []
    }


def extract_entities_with_llm(title: str, abstract: str, model: str = "phi3:mini") -> dict:
    """
    Extract entities using an LLM via Ollama.

    Args:
        title: Article title
        abstract: Article abstract
        model: Ollama model to use

    Returns:
        Dictionary with entity lists
    """
    # Build prompt
    prompt = ENTITY_EXTRACTION_PROMPT.format(
        title=title or "No title",
        abstract=abstract or "No abstract"
    )

    # Call LLM
    print(f"    Calling {model}...")
    response = call_ollama(prompt, model=model)

    # Extract JSON from response
    entities = extract_json_from_response(response)

    return entities


def process_medline_with_ollama(
    input_file: str,
    output_dir: str,
    model: str = "phi3:mini"
):
    """
    Process MEDLINE file using Ollama LLM.

    Args:
        input_file: Path to MEDLINE file
        output_dir: Directory to save output files
        model: Ollama model to use (phi3:mini, gemma, qwen, etc.)
    """
    print(f"Processing MEDLINE file: {input_file}")
    print(f"Output directory: {output_dir}")
    print(f"Using Ollama model: {model}")
    print("=" * 70)

    # Verify Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✓ Ollama server is running")
    except requests.exceptions.RequestException:
        print("✗ ERROR: Ollama server is not running!")
        print("  Please start Ollama with: ollama serve")
        return

    # Verify model is available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]

        if model not in model_names and not any(model in m for m in model_names):
            print(f"✗ ERROR: Model '{model}' not found!")
            print(f"  Available models: {model_names}")
            print(f"  Pull the model with: ollama pull {model}")
            return
        print(f"✓ Model '{model}' is available")
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not verify model availability: {e}")

    print("=" * 70)

    # Parse MEDLINE file
    records = parse_medline_file(input_file)
    print(f"\nFound {len(records)} MEDLINE records")

    # Process each record
    results = []
    for i, record in enumerate(records, 1):
        print(f"\nProcessing record {i}/{len(records)}...")
        print(f"  PMID: {record.get('pmid', 'Unknown')}")

        # Extract entities using LLM
        try:
            entities = extract_entities_with_llm(
                record.get('title', ''),
                record.get('abstract', ''),
                model=model
            )

            print(f"  Extracted: {len(entities['diseases'])} diseases, "
                  f"{len(entities['genes'])} genes, "
                  f"{len(entities['drugs'])} drugs, "
                  f"{len(entities['symptoms'])} symptoms")

        except Exception as e:
            print(f"  ERROR extracting entities: {e}")
            entities = {
                'diseases': [],
                'genes': [],
                'drugs': [],
                'symptoms': []
            }

        # Create JSON
        result = create_entity_json(
            pmid=record.get('pmid'),
            title=record.get('title'),
            abstract=record.get('abstract'),
            diseases=entities['diseases'],
            genes=entities['genes'],
            drugs=entities['drugs'],
            symptoms=entities['symptoms']
        )

        # Validate
        valid, errors = validate_entity_json(result)
        if not valid:
            print(f"  Warning: Validation errors: {errors}")

        results.append(result)

        # Save individual record
        pmid = record.get('pmid', f'record_{i}')
        output_file = os.path.join(output_dir, f'pmid_{pmid}_ollama.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_to_string(result))
        print(f"  Saved to: {output_file}")

    # Save combined results
    combined_file = os.path.join(output_dir, f'all_records_ollama_{model.replace(":", "_")}.json')
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n{'=' * 70}")
    print(f"Combined results saved to: {combined_file}")

    # Create summary
    summary = {
        'processing_date': datetime.now().isoformat(),
        'input_file': input_file,
        'model_used': model,
        'total_records': len(records),
        'records_processed': len(results),
        'summary': {
            'total_diseases': sum(len(r['entities']['diseases']) for r in results),
            'total_genes': sum(len(r['entities']['genes']) for r in results),
            'total_drugs': sum(len(r['entities']['drugs']) for r in results),
            'total_symptoms': sum(len(r['entities']['symptoms']) for r in results),
        }
    }

    summary_file = os.path.join(output_dir, f'processing_summary_ollama_{model.replace(":", "_")}.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Processing summary saved to: {summary_file}")

    # Print summary
    print(f"\n{'=' * 70}")
    print("PROCESSING SUMMARY")
    print(f"{'=' * 70}")
    print(f"Model used: {model}")
    print(f"Records processed: {summary['total_records']}")
    print(f"Total diseases extracted: {summary['summary']['total_diseases']}")
    print(f"Total genes extracted: {summary['summary']['total_genes']}")
    print(f"Total drugs extracted: {summary['summary']['total_drugs']}")
    print(f"Total symptoms extracted: {summary['summary']['total_symptoms']}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    import sys

    # Process the sample MEDLINE file
    input_file = '../data/sample_medline.txt'
    output_dir = '../output'

    # Get model from command line argument or use default
    model = sys.argv[1] if len(sys.argv) > 1 else "phi3:mini"

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process the file
    process_medline_with_ollama(input_file, output_dir, model=model)

    print("\n✓ Processing complete!")
    print(f"\nOutput files are in: {os.path.abspath(output_dir)}")
    print(f"\nTo use a different model, run:")
    print(f"  python3 process_medline_ollama.py gemma")
    print(f"  python3 process_medline_ollama.py qwen")

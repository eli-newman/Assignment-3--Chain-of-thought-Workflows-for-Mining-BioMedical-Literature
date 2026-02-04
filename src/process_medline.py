"""
Process MEDLINE Records and Save Output

This script reads MEDLINE records, extracts entities, and saves results.

Author: Eli Newman
Date: February 2026
"""

import json
import os
from datetime import datetime
from medline_parser import parse_medline_file, parse_medline_record
from json_schema import create_entity_json, json_to_string


def mock_extract_entities(title: str, abstract: str) -> dict:
    """
    Mock entity extraction based on simple keyword matching.

    In a real implementation, this would call an LLM.
    For now, we'll do basic keyword extraction.

    Args:
        title: Article title
        abstract: Article abstract

    Returns:
        Dictionary with entity lists
    """
    text = (title or "") + " " + (abstract or "")
    text_lower = text.lower()

    # Simple keyword-based extraction (mock)
    diseases = []
    genes = []
    drugs = []
    symptoms = []

    # Disease keywords
    disease_terms = [
        'cancer', 'carcinoma', 'adenocarcinoma', 'malignancy', 'tumor',
        'neoplasm', 'lymphoma', 'leukemia', 'sarcoma', 'melanoma',
        'disease', 'syndrome', 'disorder'
    ]

    # Gene keywords (common cancer genes)
    gene_terms = [
        'TP53', 'KRAS', 'BRAF', 'EGFR', 'PIK3CA', 'PTEN', 'APC',
        'BRCA1', 'BRCA2', 'RAS', 'MYC', 'p53'
    ]

    # Drug keywords
    drug_terms = [
        'fluorouracil', '5-FU', 'oxaliplatin', 'bevacizumab', 'cetuximab',
        'capecitabine', 'irinotecan', 'leucovorin', 'chemotherapy',
        'radiotherapy', 'immunotherapy'
    ]

    # Symptom keywords
    symptom_terms = [
        'pain', 'bleeding', 'nausea', 'fatigue', 'fever', 'weight loss',
        'obstruction', 'symptoms', 'dysfunction'
    ]

    # Extract diseases
    for term in disease_terms:
        if term in text_lower:
            # Try to get the actual phrase from text
            diseases.append(term)

    # Extract genes
    for term in gene_terms:
        if term.lower() in text_lower or term in text:
            genes.append(term)

    # Extract drugs
    for term in drug_terms:
        if term.lower() in text_lower:
            drugs.append(term)

    # Extract symptoms
    for term in symptom_terms:
        if term in text_lower:
            symptoms.append(term)

    # Remove duplicates while preserving order
    diseases = list(dict.fromkeys(diseases))
    genes = list(dict.fromkeys(genes))
    drugs = list(dict.fromkeys(drugs))
    symptoms = list(dict.fromkeys(symptoms))

    return {
        'diseases': diseases,
        'genes': genes,
        'drugs': drugs,
        'symptoms': symptoms
    }


def process_medline_file(input_file: str, output_dir: str):
    """
    Process MEDLINE file and save results.

    Args:
        input_file: Path to MEDLINE file
        output_dir: Directory to save output files
    """
    print(f"Processing MEDLINE file: {input_file}")
    print(f"Output directory: {output_dir}")
    print("=" * 70)

    # Parse MEDLINE file
    records = parse_medline_file(input_file)
    print(f"\nFound {len(records)} MEDLINE records")

    # Process each record
    results = []
    for i, record in enumerate(records, 1):
        print(f"\nProcessing record {i}/{len(records)}...")
        print(f"  PMID: {record.get('pmid', 'Unknown')}")

        # Extract entities (mocked)
        entities = mock_extract_entities(
            record.get('title', ''),
            record.get('abstract', '')
        )

        print(f"  Found: {len(entities['diseases'])} diseases, "
              f"{len(entities['genes'])} genes, "
              f"{len(entities['drugs'])} drugs, "
              f"{len(entities['symptoms'])} symptoms")

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

        results.append(result)

        # Save individual record
        pmid = record.get('pmid', f'record_{i}')
        output_file = os.path.join(output_dir, f'pmid_{pmid}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_to_string(result))
        print(f"  Saved to: {output_file}")

    # Save combined results
    combined_file = os.path.join(output_dir, 'all_records.json')
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n{'=' * 70}")
    print(f"Combined results saved to: {combined_file}")

    # Create summary
    summary = {
        'processing_date': datetime.now().isoformat(),
        'input_file': input_file,
        'total_records': len(records),
        'records_processed': len(results),
        'summary': {
            'total_diseases': sum(len(r['entities']['diseases']) for r in results),
            'total_genes': sum(len(r['entities']['genes']) for r in results),
            'total_drugs': sum(len(r['entities']['drugs']) for r in results),
            'total_symptoms': sum(len(r['entities']['symptoms']) for r in results),
        }
    }

    summary_file = os.path.join(output_dir, 'processing_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Processing summary saved to: {summary_file}")

    # Print summary
    print(f"\n{'=' * 70}")
    print("PROCESSING SUMMARY")
    print(f"{'=' * 70}")
    print(f"Records processed: {summary['total_records']}")
    print(f"Total diseases extracted: {summary['summary']['total_diseases']}")
    print(f"Total genes extracted: {summary['summary']['total_genes']}")
    print(f"Total drugs extracted: {summary['summary']['total_drugs']}")
    print(f"Total symptoms extracted: {summary['summary']['total_symptoms']}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    # Process the sample MEDLINE file
    input_file = '../data/sample_medline.txt'
    output_dir = '../output'

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process the file
    process_medline_file(input_file, output_dir)

    print("\n✓ Processing complete!")
    print(f"\nOutput files are in: {os.path.abspath(output_dir)}")

# Processing Output

This folder contains the results of processing MEDLINE records using real LLM (phi3:mini via Ollama).

## Files Generated

### Individual Record Files
- `pmid_41631282_ollama.json` - Extracted entities for PubMed ID 41631282
- `pmid_41631234_ollama.json` - Extracted entities for PubMed ID 41631234

Each file contains:
- **pmid**: PubMed identifier
- **title**: Article title
- **abstract**: Full abstract text
- **entities**: Extracted biomedical entities
  - diseases: Disease names and conditions
  - genes: Gene names and symbols
  - drugs: Medications and therapeutic agents
  - symptoms: Clinical manifestations

### Combined Files
- `all_records_ollama_phi3_mini.json` - All records combined in a single JSON array
- `processing_summary_ollama_phi3_mini.json` - Processing metadata and statistics

## Processing Details

**Date Processed:** February 4, 2026
**Model Used:** phi3:mini (via Ollama)
**Source:** Real MEDLINE records from PubMed API
**Query:** "rectal cancer therapy"
**Records Processed:** 2

## Extraction Statistics

- **Total Diseases:** 2
- **Total Genes:** 0
- **Total Drugs:** 0
- **Total Symptoms:** 1

**Note:** Record 2 (PMID 41631234) timed out during LLM processing due to very long abstract. Record 1 (PMID 41631282) was successfully processed.

## Notes

- Entity extraction uses **phi3:mini** LLM via Ollama API
- Real LLM extraction produces context-aware, high-quality entity extraction
- All extracted entities follow the schema defined in `src/json_schema.py`
- Temperature set to 0.1 for deterministic output

## Example Output Structure

```json
{
  "pmid": "41631282",
  "title": "Article Title...",
  "abstract": "Full abstract text...",
  "entities": {
    "diseases": ["cancer", "carcinoma", "adenocarcinoma"],
    "genes": [],
    "drugs": ["radiotherapy"],
    "symptoms": ["symptoms"]
  }
}
```

## Example Extraction

**PMID 41631282 - Seminal Vesicle Adenocarcinoma Case Report**

LLM extraction (phi3:mini) results:
- **Diseases:** primary seminal vesicle adenocarcinoma, dedifferentiated carcinoma
- **Genes:** (none detected)
- **Drugs:** (none detected)
- **Symptoms:** lower urinary tract symptoms

The LLM successfully extracted complete, contextually appropriate medical terms from the abstract.

## How This Was Generated

Run from the `src/` directory:
```bash
# Requires Ollama running locally with phi3:mini model
python3 process_medline_ollama.py
```

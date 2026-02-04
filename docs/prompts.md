# Part 2: Prompt Design and Documentation

## 2.1 Prompt Set (Model-Agnostic)

### Prompt 1: MEDLINE Parsing Prompt

```
You are a medical text parser. Extract the PMID, title, and abstract from the following MEDLINE record.

MEDLINE records use specific tags:
- PMID- : PubMed ID (unique identifier)
- TI  - : Title (can span multiple lines)
- AB  - : Abstract (can span multiple lines)

Continuation lines are indented with spaces. Extract the complete text for each field.

MEDLINE Record:
{medline_record}

Return ONLY a JSON object with this exact structure:
{{
  "pmid": "extracted PMID",
  "title": "extracted title",
  "abstract": "extracted abstract"
}}

If a field is missing, use null for that field.
```

### Prompt 2: Entity Extraction Prompt

```
You are a biomedical entity extraction specialist. Analyze the following medical text and identify all relevant biomedical entities.

Extract the following entity types:
1. DISEASES: Any disease, condition, or pathology mentioned (e.g., cancer, carcinoma, adenocarcinoma, malignancy)
2. GENES: Gene names and symbols (e.g., TP53, KRAS, BRCA1)
3. DRUGS: Medications, therapeutic agents, or compounds (e.g., fluorouracil, bevacizumab, oxaliplatin)
4. SYMPTOMS: Clinical manifestations or symptoms (e.g., pain, bleeding, obstruction)

Text to analyze:
{text}

Instructions:
- Extract exact phrases as they appear in the text
- Include multi-word entities (e.g., "rectal cancer" not just "cancer")
- Do not include general medical terms unless they are specific conditions
- If an entity appears multiple times, list it only once

Return ONLY a JSON object with this structure:
{{
  "diseases": [],
  "genes": [],
  "drugs": [],
  "symptoms": []
}}
```

### Prompt 3: JSON Formatting Prompt

```
You are a data formatting specialist. Structure the following extracted information into the required JSON schema.

Input data:
{extracted_data}

Create a JSON object with this exact schema:
{{
  "pmid": "PubMed ID as string",
  "title": "Article title",
  "abstract": "Full abstract text",
  "entities": {{
    "diseases": ["list of disease names"],
    "genes": ["list of gene names"],
    "drugs": ["list of drug names"],
    "symptoms": ["list of symptoms"]
  }}
}}

Requirements:
- All keys must be present
- Use empty lists [] for entity types with no entries
- Use null for missing pmid, title, or abstract
- Ensure valid JSON syntax
- Do not add any fields not in the schema

Return ONLY the JSON object, no additional text.
```

### Prompt 4: Meta-Prompt (Chain-of-Thought)

```
You are a biomedical text mining assistant. I will give you a MEDLINE record, and you will extract structured information from it.

Follow this reasoning process:

STEP 1: Parse the record
- Identify the PMID- tag and extract the ID
- Find the TI  - tag and extract the complete title (including continuation lines)
- Find the AB  - tag and extract the complete abstract (including continuation lines)

STEP 2: Analyze the text
- Read the title and abstract carefully
- Identify medical terminology
- Consider context for each term

STEP 3: Extract entities
- Diseases: Look for pathologies, conditions, cancers
- Genes: Look for gene names (usually capitalized abbreviations)
- Drugs: Look for medication names (brand or generic)
- Symptoms: Look for clinical manifestations

STEP 4: Structure the output
- Combine all information into the required JSON format
- Validate that all required fields are present
- Ensure no duplicate entities

MEDLINE Record:
{medline_record}

Think through each step, then provide your final answer as a JSON object with this structure:
{{
  "pmid": "...",
  "title": "...",
  "abstract": "...",
  "entities": {{
    "diseases": [],
    "genes": [],
    "drugs": [],
    "symptoms": []
  }}
}}

Begin your reasoning:
```

## 2.2 Prompt Rationale

### Prompt 1: MEDLINE Parsing Prompt

**Design rationale:**
- **Explicit tag definitions**: Models might not know MEDLINE format, so I define the tags
- **Continuation line hint**: Critical for multi-line fields
- **JSON-only output**: Prevents the model from adding explanatory text
- **Null handling**: Tells the model how to handle missing fields

**Anticipated failure modes:**
1. **Incomplete multi-line extraction**: Model might only get first line of abstract
   - **Mitigation**: Explicitly mention "can span multiple lines" and "continuation lines are indented"
2. **Extra fields in JSON**: Model might add confidence scores or other data
   - **Mitigation**: "Return ONLY" and show exact structure
3. **String formatting issues**: Quotes, newlines causing invalid JSON
   - **Mitigation**: Will need post-processing validation

**Refinement plans:**
- Add few-shot examples if accuracy is low
- Consider asking for step-by-step reasoning first
- Might need to specify character encoding handling

### Prompt 2: Entity Extraction Prompt

**Design rationale:**
- **Role definition**: "biomedical entity extraction specialist" primes the model
- **Numbered list**: Clear categories with examples
- **Specific instructions**: "exact phrases", "multi-word entities" prevents common errors
- **Deduplication**: "list it only once" reduces redundancy

**Anticipated failure modes:**
1. **Over-extraction**: Model might extract common words like "the lead researcher"
   - **Mitigation**: "Do not include general medical terms unless they are specific conditions"
   - **Refinement**: May need to add negative examples
2. **Under-extraction**: Model might miss abbreviations
   - **Mitigation**: Current prompt doesn't explicitly handle this - would add example like "PSA (prostate-specific antigen)"
3. **Inconsistent normalization**: "cancer" vs "Cancer" vs "cancers"
   - **Mitigation**: "Extract exact phrases as they appear" - decided not to normalize yet

**Refinement plans:**
- Add few-shot examples showing good vs bad extractions
- Consider asking model to explain its reasoning for borderline cases
- Might add confidence scores in future iteration

### Prompt 3: JSON Formatting Prompt

**Design rationale:**
- **Single responsibility**: This prompt just formats, doesn't extract
- **Schema repetition**: Showing exact structure multiple times
- **Validation rules**: "All keys must be present", "valid JSON syntax"
- **Strict output**: "Return ONLY the JSON object, no additional text"

**Anticipated failure modes:**
1. **Missing keys**: Model might omit empty fields
   - **Mitigation**: "All keys must be present", "Use empty lists []"
2. **Invalid JSON**: Trailing commas, unescaped quotes
   - **Mitigation**: "Ensure valid JSON syntax" - but will still need validation
3. **Added commentary**: Model explains what it did
   - **Mitigation**: "Return ONLY" - emphasized twice

**Refinement plans:**
- If failures persist, provide example of correct output
- Consider using structured output if model supports it
- May add JSON schema validation instructions

### Prompt 4: Meta-Prompt (Chain-of-Thought)

**Design rationale:**
- **Explicit reasoning steps**: Breaks task into manageable pieces
- **Guided thinking**: Each step has clear objectives
- **Progressive complexity**: Parse → Analyze → Extract → Structure
- **"Think then answer" pattern**: "Begin your reasoning" encourages step-by-step

**Anticipated failure modes:**
1. **Skipping reasoning**: Model might jump to answer
   - **Mitigation**: "Think through each step" - may need to be more explicit
   - **Refinement**: Could require model to show reasoning before answer
2. **Verbose output**: Long explanations before JSON
   - **Mitigation**: Acceptable for this prompt - reasoning is valuable
   - **Refinement**: Could separate reasoning and final answer sections
3. **Inconsistent quality**: Sometimes good reasoning, sometimes not
   - **Mitigation**: Test and iterate on step descriptions

**Refinement plans:**
- Compare accuracy with/without chain-of-thought
- Analyze where reasoning helps vs doesn't
- Consider making this the default for complex records
- Might add examples of good reasoning

## Cross-Cutting Concerns

### Model-Agnostic Design
All prompts avoid model-specific features:
- No references to "ChatGPT" or specific model capabilities
- Standard instruction format
- No reliance on special tokens or formatting

### Consistency
- All prompts use "Return ONLY" pattern
- JSON structure is identical across prompts
- Entity categories defined identically

### Future Enhancements
1. **Few-shot examples**: Add 1-2 examples to each prompt
2. **Error recovery**: Add instructions for handling malformed input
3. **Confidence scores**: Ask model to rate certainty
4. **Batch processing**: Adapt prompts for multiple records
5. **Validation instructions**: Add JSON schema for models that support it

## Testing Strategy

For each prompt:
1. Test with sample MEDLINE record
2. Evaluate with all three models (Gemma, Phi, Qwen)
3. Compare outputs
4. Identify model-specific failure patterns
5. Refine prompt or add model-specific variations if needed

Success metrics:
- **Parsing**: 100% accuracy on required fields
- **Entity extraction**: High precision (>80%), acceptable recall (>60%)
- **JSON formatting**: 100% valid JSON
- **Chain-of-thought**: Measurably better accuracy vs non-CoT

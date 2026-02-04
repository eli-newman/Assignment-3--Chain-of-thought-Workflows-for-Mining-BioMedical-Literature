# Part 1: Chain-of-Thought Documentation

## 1.1 Reasoning and Process Notes

### How I Think About Parsing MEDLINE Records

When I first looked at MEDLINE records, I noticed they have a very structured format with specific tags like `PMID-`, `TI  -`, `AB  -`. My reasoning process:

1. **Pattern Recognition**: Each field starts with a tag (2-4 characters) followed by a dash and optional spaces
2. **Multi-line Handling**: Fields like abstracts (AB) can span multiple lines - continuation lines are indented
3. **Required vs Optional Fields**: Not all records have all fields (e.g., some might not have abstracts)

**My approach:**
- Parse line-by-line, tracking the current field
- When I see a new tag, save the previous field and start a new one
- For continuation lines (indented), append to the current field
- Handle missing fields gracefully with None or empty strings

**Why this matters:** If I don't handle multi-line fields correctly, I'll lose important information. The abstract is often the most valuable part for entity extraction.

### How I Think About Extracting Biomedical Entities

This is where it gets interesting. I need to identify:
- **Diseases**: cancer, carcinoma, adenocarcinoma, malignancy
- **Genes**: Specific gene names (often capitalized, like TP53, KRAS)
- **Drugs**: Medication names (can be brand or generic)
- **Symptoms**: Clinical manifestations

**My reasoning:**
1. **Context matters**: "lead" could be a verb or the element Pb - LLMs are good at disambiguation
2. **Abbreviations**: Medical text is full of abbreviations (PSA, MRI, ctDNA)
3. **Multi-word entities**: "prostate-specific antigen" is one entity, not three

**Strategy:**
- Use the LLM's pre-training on medical text
- Provide examples in the prompt (few-shot learning)
- Ask the model to think step-by-step before extracting
- Request confidence scores if possible

**Potential issues:**
- False positives (extracting common words as medical terms)
- Missing entities that use non-standard terminology
- Boundary detection (where does an entity start/end?)

### How I Think About Structuring JSON Outputs

I want a consistent schema that's easy to work with downstream. My thought process:

1. **Top-level metadata**: PMID, title, abstract (verbatim from source)
2. **Nested entities**: Group by type in a sub-object
3. **Lists for multiple instances**: A paper might mention multiple diseases

**Design decisions:**
```json
{
  "pmid": "string - unique identifier",
  "title": "string - exact title",
  "abstract": "string - full abstract text",
  "entities": {
    "diseases": ["list of strings"],
    "genes": ["list of strings"],
    "drugs": ["list of strings"],
    "symptoms": ["list of strings"]
  }
}
```

**Rationale:**
- **Flat structure for metadata**: Easy to access PMID directly
- **Nested entities**: Keeps things organized, prevents naming conflicts
- **Arrays**: Allow multiple entities per type
- **String values**: Simple and flexible (could add metadata later)

**Trade-offs I considered:**
- Could add entity positions (character offsets) - decided against for simplicity
- Could add confidence scores - maybe in future iteration
- Could normalize entity names (e.g., "5-FU" → "fluorouracil") - too complex for now

### How I Expect the Models (Gemma, Phi, Qwen) to Behave

Based on what I know about these models:

**Gemma (Google)**
- Strength: Strong at instruction following
- Expectation: Will likely follow JSON format precisely
- Concern: Might be overly conservative (miss some entities to avoid false positives)

**Phi (Microsoft)**
- Strength: Good reasoning capabilities for its size
- Expectation: Should handle chain-of-thought prompting well
- Concern: Smaller model might miss complex medical terminology

**Qwen (Alibaba)**
- Strength: Multilingual training (might help with Latin medical terms)
- Expectation: Good balance of precision and recall
- Concern: Less familiar with this model's behavior

**Universal expectations:**
1. All should benefit from clear, structured prompts
2. Few-shot examples will improve consistency
3. Chain-of-thought reasoning will improve accuracy
4. JSON formatting might need validation/correction

**Testing strategy:**
- Start with same prompt for all three
- Compare outputs on identical input
- Adjust prompts if one model consistently underperforms
- Track failure modes (hallucinations, missed entities, format errors)

## Key Insights

1. **Parsing is deterministic, extraction is probabilistic**: I can write unit tests for parsing, but entity extraction needs human evaluation
2. **Prompt engineering is iterative**: My first prompts won't be perfect
3. **Edge cases matter**: Empty abstracts, non-English text, special characters
4. **Model-agnostic design**: If I switch from Qwen to GPT-4 later, only the API call changes

## Open Questions

- Should I lowercase entity names for consistency?
- How to handle gene/protein ambiguity (e.g., p53 vs TP53)?
- What if the LLM returns incomplete JSON?
- Do I need a confidence threshold for including entities?

These will be answered through testing and iteration.

# Assignment 3: Chain-of-Thought Workflows for Mining BioMedical Literature

**Student:** Eli Newman
**Date:** February 3, 2026
**Course:** Topics in Computer Science: Theory and Applications of LLMs

## Overview

This project implements modular components for PubMed text mining using multiple LLMs (Gemma, Phi, Qwen) via Ollama. We used the phi3:mini model for processing. The focus is on chain-of-thought reasoning, prompt design, and testing individual components.

## Project Structure

```
├── docs/
│   ├── chain_of_thought.md          # Part 1: Reasoning documentation
│   └── prompts.md                    # Part 2: Prompt set and rationale
├── src/
│   ├── medline_parser.py             # MEDLINE parsing component
│   ├── json_schema.py                # JSON schema helper
│   └── model_example.py              # Example model call (mocked)
├── tests/
│   ├── test_medline_parser.py        # Tests for parser
│   └── test_json_schema.py           # Tests for JSON schema
├── data/
│   └── sample_medline.txt            # Sample MEDLINE records from PubMed
└── README.md                          # This file
```

## Running the Code

### Install Dependencies
```bash
pip install pytest
```

### Run Tests
```bash
pytest tests/
```

### Run Example
```bash
python src/model_example.py
```

## Key Features

- **Model-agnostic prompts**: Work with Gemma, Phi, and Qwen via Ollama
- **Modular components**: Separate parsing, schema construction, and model interaction
- **Comprehensive testing**: Unit tests for all components
- **Real data**: Uses actual MEDLINE records from PubMed API
- **Local LLM processing**: Uses Ollama for local model execution

## Documentation

See `docs/` folder for detailed documentation on:
- Chain-of-thought reasoning process
- Prompt design and rationale
- Expected model behaviors

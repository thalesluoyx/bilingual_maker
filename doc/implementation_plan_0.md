# Project Proposal: Professional Astronomy PDF to Bilingual ePUB

## Goal Description
The objective is to create a robust pipeline that converts professional Astronomy English PDFs into high-quality English-Chinese bilingual ePUB e-books. The system will leverage Large Language Models (LLMs) for accurate translation, specifically tuned for astronomy terminology, and ensure the final output preserves the original layout structure (images, formulas) as much as possible.

## User Review Required
> [!IMPORTANT]
> **PDF Parsing Tool**: The proposal assumes the use of `Magic-PDF` (MinerU) or a similar high-quality PDF-to-Markdown tool, given the workspace context. Please confirm if this is the intended tool.
> **Model Selection**: The user has requested to use an external intelligent API. The system will be configured to use an OpenAI-compatible API (e.g., GPT-4, Claude, DeepSeek) via API Key.
> **Cost**: External APIs are paid services. Ensure an API Key is available.

## Proposed Changes

### 1. Architecture Overview
The project will be structured into modular components:
- **Parser**: Extracts content from PDF to structured Markdown.
- **Text Processor**: Splits Markdown into translatable chunks while preserving structure (code blocks, math, images).
- **Translator**: Async wrapper for LLM API (Ollama) with retry logic and glossary support.
- **Builder**: Reconstructs bilingual Markdown and converts it to ePUB.

### 2. Component Details

#### A. PDF Parsing (`pdf_parser.py`)
- **Input**: PDF File.
- **Action**: Utilize `magic-pdf` (or existing JSON outputs in `old_version`) to generate high-fidelity Markdown.
- **Output**: Markdown file with images extracted to a folder.

#### B. Markdown Processing (`md_processor.py`)
- **Improvement over [translator.py](file:///e:/Work/workspace/magic-pdf_wkr/old_version/output_1/1/auto/translator.py)**:
    - Instead of simple line-by-line reading, use a state-machine or AST-based approach to identify:
        - Headers (Keep as is, maybe translate title)
        - Paragraphs (Translate)
        - Code Blocks / Math Blocks (Skip translation, preserve formatting)
        - Images (Preserve links)
        - Lists/Tables (Handle carefully to maintain alignment)
    - **Chunking**: Group small lines to form complete sentences/paragraphs for better translation context.

#### C. Translation Engine ([translator.py](file:///e:/Work/workspace/magic-pdf_wkr/old_version/output_1/1/auto/translator.py))
- **Asyncio**: Use Python `asyncio` to send multiple requests in parallel.
- **API Integration**: Support OpenAI-compatible API format (Base URL + API Key).
- **Prompt Engineering**:
    - Inject an "Astronomy Glossary" into the system prompt.
    - Maintain "Strict Mode" to avoid conversational filler.
- **Error Handling**: Retry mechanism for timeouts or rate limits (429 errors).

#### D. ePUB Generator (`epub_maker.py`)
- **Bilingual Formatting**:
    - Format: `[English Paragraph] \n\n [中文翻译]`.
    - Optional: Use HTML/CSS within ePUB to style the Chinese text (e.g., slightly different color or font size) for better distinction.
- **Tooling**: Use `pandoc` to compile the final ePUB, ensuring images are embedded.

### 3. Directory Structure
```text
project_root/
├── config.py           # Configuration (Model, API URL, Prompts)
├── main.py             # Entry point
├── core/
│   ├── parser.py       # PDF -> MD
│   ├── processor.py    # MD parsing & chunking
│   ├── translator.py   # LLM interaction
│   └── epub.py         # MD -> ePUB
├── assets/             # Glossaries, styles
├── output/             # Final results
├── input/              # Input files
└── tests/              # Tests
```

## Verification Plan

### Automated Tests
- **pytest**: Use `pytest` to run unit tests.
- **Unit Tests**: Test the Markdown splitter to ensure it doesn't break code blocks or math formulas.
- **Mock Translation**: Run the pipeline with a "Mock" translator (returns "Translated: [Text]") to verify the file structure and ePUB generation without waiting for the LLM.

### Manual Verification
- **Visual Check**: Open the generated ePUB in a reader (Apple Books, Calibre) to check:
    - Image rendering.
    - Math formula rendering (LaTeX support in ePUBs can be tricky; might need conversion to SVG or MathML).
    - Bilingual text alignment.

# Bilingual ePUB Maker

Convert English astronomy PDFs into high-quality English-Chinese bilingual ePUB e-books with AI-powered translation.

## Features

- 📄 **PDF to Markdown**: Converts PDFs using `magic-pdf` with structure preservation
- 🌐 **AI Translation**: Uses LLM APIs (OpenAI-compatible) for accurate translation
- 📚 **Astronomy Glossary**: Integrated 29,936 astronomy terms for consistent terminology
- 📖 **Bilingual ePUB**: Generates professional ePUB files with side-by-side translations
- 💾 **State Management**: Resume interrupted workflows with automatic state saving
- ⚙️ **Flexible Pipeline**: Run specific steps or entire workflow

## Installation

### Prerequisites

- Python 3.10+
- Pandoc (for ePUB generation)
- magic-pdf (for PDF parsing)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/thalesluoyx/bilingual_maker.git
cd bilingual_maker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your LLM API:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

Required environment variables in `.env`:
```
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

## Usage

### Basic Usage

Convert a PDF to bilingual ePUB:
```bash
python main.py input/document.pdf
```

### Advanced Options

**Specify output directory:**
```bash
python main.py input/document.pdf --output my_output
```

**Define step order**
| Step | Name                 | Description                               |
| ---- | -------------------- | ----------------------------------------- |
| 0    | prepare_paths        | Prepare paths and directories             |
| 1    | pdf_to_markdown      | Convert PDF to Markdown (if input is PDF) |
| 2    | read_markdown        | Read Markdown file                        |
| 3    | parse_markdown       | Parse and chunk Markdown into blocks      |
| 4    | identify_text_blocks | Identify text blocks to translate         |
| 4.1  | load_glossary        | Load astronomy glossary                   |
| 5    | translate            | Translate text blocks using LLM           |
| 6    | merge_translations   | Merge translations back into blocks       |
| 7    | reconstruct_markdown | Reconstruct bilingual Markdown            |
| 8    | generate_epub        | Generate ePUB from bilingual Markdown     |
        

**Run specific steps:**
```bash
# Steps 0-4: Parse PDF and prepare for translation
python main.py input/document.pdf --steps 0-4

# Steps 5-7: Translate and create bilingual markdown (resume from previous state)
python main.py input/document.pdf --steps 5-7 --resume

# Step 8: Generate ePUB only
python main.py input/document.pdf --steps 8 --resume
```

**check pipeline status:**
```bash
python main.py input/document.pdf --check
```

**Use presets:**
```bash
# Prepare only (parse PDF, no translation)
python main.py input/document.pdf --preset prepare_only

# Translate only (requires previous preparation)
python main.py input/document.pdf --preset translate_only --resume

```

## Glossary

The system includes an astronomy glossary (`assets/astrodict241020_ec.txt`) with 29,936 terms. The glossary ensures consistent translation of technical terms:

- **Case-insensitive matching**: `redshift`, `RedShift`, `Redshift` → `红移`
- **Contextual extraction**: Only relevant terms are included in translation prompts
- **Automatic integration**: No manual configuration needed

## Testing

Run all tests:
```bash
python -m pytest
```

Run specific test suites:
```bash
# Test glossary integration
python -m pytest tests/test_glossary.py -s

# Test LLM connectivity
python -m pytest tests/test_llm_connectivity.py -s

# Test markdown processor
python -m pytest tests/test_processor.py
```

## Configuration

Edit `config.py` to customize:

- **API settings**: Model, base URL, timeout, retry attempts
- **Pipeline steps**: Enable/disable specific steps
- **System prompt**: Modify translation instructions
- **Glossary**: Add custom astronomy terms

## Troubleshooting

**PDF parsing fails:**
- Ensure `magic-pdf` is installed correctly
- Check PDF is not encrypted or corrupted

**Translation errors:**
- Verify API key and base URL in `.env`
- Check API rate limits and quotas
- Review `config.py` timeout settings

**ePUB generation fails:**
- Ensure Pandoc is installed: `pandoc --version`
- Check bilingual markdown file exists

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
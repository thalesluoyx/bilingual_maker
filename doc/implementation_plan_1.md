# Pipeline Step Configuration

## Goal

Allow users to configure which pipeline steps to run through `config.py`, enabling incremental processing and result verification between steps.

## Current Pipeline Steps

Based on `main.py`, the pipeline has these steps:

- **Step 0**: Prepare paths and directories
- **Step 1**: PDF to Markdown conversion (if input is PDF)
- **Step 2**: Read Markdown file
- **Step 3**: Parse & chunk Markdown into blocks
- **Step 4**: Identify text blocks to translate
- **Step 4.1**: Load glossary
- **Step 5**: Translate text blocks using LLM
- **Step 6**: Merge translations back into blocks
- **Step 7**: Reconstruct bilingual Markdown
- **Step 8**: Generate ePUB from bilingual Markdown

## User Requirements

> [!IMPORTANT]
> User wants to run steps in stages:
> 1. Run steps 0-4, check results
> 2. Run steps 4-7, check results  
> 3. Run step 8

This requires:
- Configuration to specify which steps to run
- Ability to save/load intermediate state between runs
- Clear output indicating what was done and what's next

## Proposed Changes

### `config.py`

Add pipeline configuration:

```python
# Pipeline Step Configuration
PIPELINE_STEPS = {
    'prepare_paths': True,          # Step 0
    'pdf_to_markdown': True,         # Step 1
    'read_markdown': True,           # Step 2
    'parse_markdown': True,          # Step 3
    'identify_text_blocks': True,    # Step 4
    'load_glossary': True,           # Step 4.1
    'translate': True,               # Step 5
    'merge_translations': True,      # Step 6
    'reconstruct_markdown': True,    # Step 7
    'generate_epub': True            # Step 8
}

# Convenience presets
PIPELINE_PRESETS = {
    'prepare_only': ['prepare_paths', 'pdf_to_markdown', 'read_markdown', 'parse_markdown', 'identify_text_blocks'],
    'translate_only': ['load_glossary', 'translate', 'merge_translations'],
    'finalize_only': ['reconstruct_markdown', 'generate_epub'],
    'all': list(PIPELINE_STEPS.keys())
}
```

---

### `main.py`

Modify to:

1. **Add state persistence**:
   - Save intermediate results (blocks, translations) to JSON files
   - Load previous state if continuing from a checkpoint

2. **Add step control logic**:
   - Check `Config.PIPELINE_STEPS` before each step
   - Skip steps that are disabled
   - Print clear messages about what's being skipped

3. **Add command-line arguments**:
   - `--steps`: Specify which steps to run (e.g., `--steps 0-4` or `--steps translate_only`)
   - `--resume`: Resume from saved state
   - `--state-file`: Path to state file (default: `{output_dir}/pipeline_state.json`)

4. **Refactor into step functions**:
   - Extract each step into a separate function
   - Makes it easier to control execution flow

#### Example refactored structure:

```python
async def step_0_prepare_paths(input_file, output_dir):
    """Step 0: Prepare paths and directories"""
    if not Config.PIPELINE_STEPS.get('prepare_paths', True):
        print("⏭️  Skipping Step 0: Prepare paths")
        return None
    print("▶️  Step 0: Preparing paths...")
    # ... existing code ...
    return {'base_name': base_name, 'output_dir': output_dir}

async def step_1_pdf_to_markdown(input_file, output_dir, state):
    """Step 1: PDF to Markdown conversion"""
    if not Config.PIPELINE_STEPS.get('pdf_to_markdown', True):
        print("⏭️  Skipping Step 1: PDF to Markdown")
        return state
    # ... existing code ...
    state['md_file'] = md_file
    return state

# ... similar for other steps ...
```

---

### State File Format

`pipeline_state.json`:

```json
{
  "input_file": "path/to/input.pdf",
  "output_dir": "output",
  "base_name": "document",
  "md_file": "output/document.md",
  "blocks": [...],
  "text_blocks": [...],
  "translated_texts": [...],
  "bilingual_md_path": "output/document_bilingual.md",
  "last_completed_step": "merge_translations",
  "timestamp": "2025-03-27T08:41:56"
}
```

## Verification Plan

### Manual Testing

1. **Test step 0-4 only**:
   ```bash
   python main.py input.pdf --output test_output --steps 0-4
   ```
   - Verify state file is saved
   - Check that translation hasn't run yet

2. **Test resume from step 5**:
   ```bash
   python main.py input.pdf --output test_output --steps 5-7 --resume
   ```
   - Verify it loads previous state
   - Check bilingual markdown is created

3. **Test final step only**:
   ```bash
   python main.py input.pdf --output test_output --steps 8 --resume
   ```
   - Verify ePUB is generated

4. **Test presets**:
   ```bash
   python main.py input.pdf --preset prepare_only
   python main.py input.pdf --preset translate_only --resume
   python main.py input.pdf --preset finalize_only --resume
   ```

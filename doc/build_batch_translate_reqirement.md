# Requirement
Now the bilingual_maker is good, and I want to enhance it to build a bilingual pipeline maker to translate multi english pdf files one by one. Below are the detail:

## 1. Batch Processing Pipeline
- **Goal**: Enable processing of multiple PDF files in a batch.
- **Input Directory**: `input/pipeline` - Place source PDF files here.
- **Output Directory**: `output/pipeline` - Translated files and logs will be saved here.
- **Configuration**:
    - A configuration file (e.g., `batch_config.yaml` or `batch_config.json`) to specify which files to process.
    - If the config file is missing or empty, process all PDFs in `input/pipeline` by default (optional, but good for usability).
    - Support specifying a "Request ID" for the batch run.

## 2. Process Logic & Error Handling
- **Sequential Processing**: Process files one by one.
- **Error Resilience**: If a file fails to translate (e.g., parsing error, API timeout), log the error, mark it as failed, and **continue** to the next file. The pipeline must not crash.
- **State Management**: Maintain the existing state mechanism (`pipeline_state.json`) for each file so individual file processing can be resumed if needed.

## 3. Logging & Reporting
- **Overall Batch Log**: Create a summary log (e.g., `batch_run_<timestamp>.log`) in `output/pipeline` that tracks:
    - Start/End time of the batch.
    - Status of each file (Success/Fail).
    - Request No/ID for the translation task.
- **Individual File Logs**: Keep the existing detailed logging for each file (saved in its specific output folder).

## 4. Refactoring & Compatibility
- **Refactor `main.py`**: Extract the core single-file processing logic into a reusable function (e.g., `process_single_file`) to be called by both the CLI (legacy mode) and the new Batch Processor.
- **CLI Usage**:
    - Keep existing command: `python main.py input.pdf` (Single file mode).
    - Add new command/flag: `python main.py --batch batch_config.json` or `python batch_runner.py`.
- **Readme**: Update `README.md` to show the usage of the new feature.

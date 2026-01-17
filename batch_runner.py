import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from config import Config
from main import process_single_file

class BatchProcessor:
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.input_dir = Path(Config.BATCH_INPUT_DIR)
        self.output_dir = Path(Config.BATCH_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped batch run directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.batch_run_dir = self.output_dir / f"batch_run_{timestamp}"
        self.batch_run_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file remains in the main output directory
        self.batch_log_file = self.output_dir / f"batch_run_{timestamp}.log"

    def log(self, message):
        timestamp = datetime.now().isoformat()
        formatted_message = f"[{timestamp}] {message}"
        print(formatted_message)
        with open(self.batch_log_file, 'a', encoding='utf-8') as f:
            f.write(formatted_message + "\n")

    def load_config(self):
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    async def run(self):
        self.log(f"Starting batch processing...")
        self.log(f"Input Directory: {self.input_dir}")
        self.log(f"Output Directory: {self.output_dir}")

        config = self.load_config()
        files_to_process = []

        if config and 'files' in config:
            self.log(f"Loaded configuration from {self.config_file}")
            for file_entry in config['files']:
                file_path = self.input_dir / file_entry['filename']
                files_to_process.append(file_path)
        else:
            self.log("No configuration file found or empty. Scanning input directory...")
            if self.input_dir.exists():
                files_to_process = list(self.input_dir.glob("*.pdf"))
            else:
                self.log(f"Error: Input directory {self.input_dir} does not exist.")
                return

        if not files_to_process:
            self.log("No PDF files found to process.")
            return

        self.log(f"Found {len(files_to_process)} files to process.")

        success_count = 0
        fail_count = 0

        for i, file_path in enumerate(files_to_process):
            self.log(f"{'='*50}")
            self.log(f"Processing file {i+1}/{len(files_to_process)}: {file_path.name}")
            
            try:
                # Use the batch run directory as the output directory
                # magic-pdf will handle creating the subfolder for the file
                target_output_dir = self.batch_run_dir
                
                await process_single_file(
                    input_file=str(file_path),
                    output_dir=str(target_output_dir),
                    preset='all', # Default to full pipeline
                    resume=True,  # Always try to resume if state exists
                    check=False
                )
                self.log(f"✅ Successfully processed: {file_path.name}")
                success_count += 1
            except Exception as e:
                self.log(f"❌ Failed to process: {file_path.name}")
                self.log(f"Error: {str(e)}")
                fail_count += 1
            
            # Add a small delay between files to be safe?
            await asyncio.sleep(1)

        self.log(f"{'='*50}")
        self.log("Batch processing completed.")
        self.log(f"Total: {len(files_to_process)}, Success: {success_count}, Failed: {fail_count}")
        self.log(f"Log saved to: {self.batch_log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Bilingual ePUB Maker")
    parser.add_argument("--config", help="Path to batch configuration file (json)")
    args = parser.parse_args()

    processor = BatchProcessor(args.config)
    asyncio.run(processor.run())

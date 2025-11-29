import asyncio
import argparse
import os
from pathlib import Path
from config import Config
from core.parser import PDFParser
from core.processor import MarkdownProcessor
from core.translator import Translator
from core.epub import EpubGenerator

async def main():
    parser = argparse.ArgumentParser(description="Bilingual ePUB Maker")
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output", help="Output directory (overrides config)")
    parser.add_argument("--preset", default="all", choices=list(Config.PIPELINE_PRESETS.keys()), help="Pipeline preset to run")
    parser.add_argument("--steps", help="Specific steps to run (e.g., '0-4' or '5')")
    
    args = parser.parse_args()

    # Override config if output dir is specified
    if args.output:
        Config.OUTPUT_DIR = args.output
    
    # Configure pipeline steps
    if args.steps:
        Config.enable_steps(args.steps)
    else:
        Config.apply_preset(args.preset)
        
    print(f"Starting pipeline for: {args.input_file}")
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return

    # State variables
    md_file = None
    blocks = None
    
    # 1. Parse PDF
    if Config.PIPELINE_STEPS.get('pdf_to_markdown'):
        print("Step 1: Parsing PDF...")
        pdf_parser = PDFParser()
        try:
            md_file = pdf_parser.parse(str(input_path))
            print(f"Markdown generated at: {md_file}")
        except Exception as e:
            print(f"PDF Parsing failed: {e}")
            return
    else:
        # Try to find existing markdown
        # Assuming standard structure: output/{filename}/{filename}.md
        # Or just check if input is MD?
        if input_path.suffix.lower() == '.md':
            md_file = str(input_path)
        else:
            # Guess path
            possible_path = Path(Config.OUTPUT_DIR) / input_path.stem / f"{input_path.stem}.md"
            # Also check magic-pdf structure: output/{stem}/auto/{stem}.md
            possible_path_auto = Path(Config.OUTPUT_DIR) / input_path.stem / "auto" / f"{input_path.stem}.md"
            
            if possible_path.exists():
                md_file = str(possible_path)
            elif possible_path_auto.exists():
                md_file = str(possible_path_auto)
            else:
                print("Skipped parsing but cannot find existing Markdown file.")
                return

    # 2. Process Markdown
    processor = MarkdownProcessor()
    if Config.PIPELINE_STEPS.get('read_markdown') or Config.PIPELINE_STEPS.get('parse_markdown'):
        print("Step 2: Processing Markdown...")
        text = processor.load_markdown(md_file)
        blocks = processor.parse(text)
        print(f"Found {len(blocks)} blocks.")

    # 3. Translate
    if Config.PIPELINE_STEPS.get('translate'):
        print("Step 3: Translating...")
        translator = Translator()
        text_blocks = [b for b in blocks if b.type == 'text']
        print(f"Translating {len(text_blocks)} text blocks...")
        
        # TODO: Load glossary if needed
        
        tasks = [translator.translate(b.content) for b in text_blocks]
        translations = await asyncio.gather(*tasks)
        
        processor.inject_translations(blocks, translations)
        print("Translation complete.")

    # 4. Reconstruct & Generate ePUB
    if Config.PIPELINE_STEPS.get('reconstruct_markdown') or Config.PIPELINE_STEPS.get('generate_epub'):
        print("Step 4: Generating ePUB...")
        
        # Reconstruct bilingual markdown
        bilingual_text = processor.reconstruct(blocks, bilingual=True)
        
        # Save bilingual markdown
        output_dir = Path(md_file).parent
        bilingual_md_path = output_dir / f"{Path(md_file).stem}_bilingual.md"
        with open(bilingual_md_path, 'w', encoding='utf-8') as f:
            f.write(bilingual_text)
        print(f"Bilingual Markdown saved to: {bilingual_md_path}")
        
        # Generate ePUB
        if Config.PIPELINE_STEPS.get('generate_epub'):
            epub_gen = EpubGenerator()
            epub_path = output_dir / f"{Path(md_file).stem}_bilingual.epub"
            try:
                epub_gen.generate(str(bilingual_md_path), str(epub_path), title=input_path.stem)
                print(f"ePUB generated successfully: {epub_path}")
            except Exception as e:
                print(f"ePUB generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

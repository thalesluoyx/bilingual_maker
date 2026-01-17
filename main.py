import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path
from tqdm.asyncio import tqdm as tqdm_asyncio
from config import Config
from core.parser import PDFParser
from core.processor import MarkdownProcessor, ContentBlock
from core.translator import Translator
from core.epub import EpubGenerator
from core.pdf import PDFGenerator
from core.state import PipelineState

class DualLogger:
    """Logger that writes to both console and file."""
    def __init__(self, log_file, resume=False):
        self.terminal = sys.stdout
        mode = 'a' if resume else 'w'
        self.log_file = open(log_file, mode, encoding='utf-8')
        self.log_file.write(f"\n{'='*80}\n")
        self.log_file.write(f"Pipeline started at: {datetime.now().isoformat()}\n")
        self.log_file.write(f"{'='*80}\n\n")
    
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        self.log_file.write(f"\n{'='*80}\n")
        self.log_file.write(f"Pipeline ended at: {datetime.now().isoformat()}\n")
        self.log_file.write(f"{'='*80}\n\n")
        self.log_file.close()

async def main():
    parser = argparse.ArgumentParser(description="Bilingual ePUB Maker")
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output", help="Output directory (overrides config)")
    parser.add_argument("--preset", default="all", choices=list(Config.PIPELINE_PRESETS.keys()), help="Pipeline preset to run")
    parser.add_argument("--steps", help="Specific steps to run (e.g., '0-4' or '5-8')")
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    parser.add_argument("--check", action="store_true", help="Check completed steps from state file")
    parser.add_argument("--state-file", help="Path to state file (default: {output_dir}/pipeline_state.json")
    parser.add_argument("--format", choices=['epub', 'pdf'], default='epub', help="Output format (epub or pdf)")
    
    args = parser.parse_args()

async def process_single_file(input_file, output_dir=None, preset='all', steps=None, resume=False, check=False, state_file=None, output_format='epub'):
    """
    Process a single PDF file through the translation pipeline.
    
    Args:
        input_file (str): Path to input PDF file
        output_dir (str, optional): Output directory. Defaults to Config.OUTPUT_DIR.
        preset (str, optional): Pipeline preset. Defaults to 'all'.
        steps (str, optional): Specific steps to run.
        resume (bool, optional): Resume from saved state. Defaults to False.
        check (bool, optional): Check completed steps. Defaults to False.
        state_file (str, optional): Path to state file.
        output_format (str, optional): Output format ('epub' or 'pdf'). Defaults to 'epub'.
    """
    # Override config if output dir is specified
    if output_dir:
        Config.OUTPUT_DIR = output_dir
        
    if output_format:
        Config.OUTPUT_FORMAT = output_format
    
    # Configure pipeline steps
    if steps:
        Config.enable_steps(steps)
    else:
        Config.apply_preset(preset)
    
    input_path = Path(input_file)
    
    # Determine output directory and setup logging
    # output_dir = Path(Config.OUTPUT_DIR) / input_path.stem
    out_dir = Path(Config.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = out_dir / f"{input_path.stem}_pipeline.log"   
    logger = DualLogger(log_file, resume=resume)
    original_stdout = sys.stdout
    sys.stdout = logger
    
    try:
        # Determine state file path
        if state_file:
            state_path = Path(state_file)
        else:
            state_path = out_dir / f"{input_path.stem}_pipeline_state.json"
        
        # Initialize state
        state_manager = PipelineState(str(state_path))
        
        if check:
            completed_steps = state_manager.get_completed_steps()
            print(f"📋 Pipeline Status for: {input_file}")
            print(f"📂 State file: {state_path}")
            if completed_steps:
                print(f"✅ Completed steps ({len(completed_steps)}):")
                for step in completed_steps:
                    print(f"  - {step}")
                print(f"⏭️  Next step: {Config.get_next_step(completed_steps[-1]) if completed_steps else 'prepare_paths'}")
            else:
                print("⚠️  No steps completed or state file not found.")
            return

        state = {}
        
        if resume:
            state = state_manager.load()
            if not state:
                print("⚠️  No saved state found. Starting from beginning.")
        
        print(f"🚀 Starting pipeline for: {input_file}")
        print(f"📋 Active steps: {[step for step, active in Config.PIPELINE_STEPS.items() if active]}")
        
        # Initialize variables from state or defaults
        md_file = state.get('md_file')
        blocks = None
        
        # Restore blocks from state if available
        if 'blocks' in state:
            blocks = [ContentBlock(**b) for b in state['blocks']]
            print(f"📂 Restored {len(blocks)} blocks from state")
        
        # Step 0: Prepare paths
        if Config.PIPELINE_STEPS.get('prepare_paths'):
            print("▶️  Step 0: Preparing paths...")
            print(f"✅ Output directory: {out_dir}")
            state['output_dir'] = str(out_dir)
            state['last_completed_step'] = 'prepare_paths'
            state_manager.save(state)
        else:
            print("⏭️  Skipping Step 0: Prepare paths")
        
        # Step 1: Parse PDF
        if Config.PIPELINE_STEPS.get('pdf_to_markdown'):
            print("▶️  Step 1: Parsing PDF...")
            if not input_path.exists():
                print(f"❌ Error: Input file not found: {input_path}")
                return
            
            pdf_parser = PDFParser()
            try:
                md_file = pdf_parser.parse(str(input_path))
                print(f"✅ Markdown generated at: {md_file}")
                
                # Extract cover image
                cover_path = Path(md_file).parent / f"{Path(md_file).stem}_bilingual_cover.png"
                if pdf_parser.extract_cover(str(input_path), str(cover_path)):
                    state['cover_image'] = str(cover_path)
                
                state['md_file'] = md_file
                state['last_completed_step'] = 'pdf_to_markdown'
                state_manager.save(state)
            except Exception as e:
                print(f"❌ PDF Parsing failed: {e}")
                raise e # Re-raise to let caller handle or just return
        else:
            if not md_file:
                # Try to find existing markdown
                if input_path.suffix.lower() == '.md':
                    md_file = str(input_path)
                else:
                    possible_path_auto = Path(Config.OUTPUT_DIR) / input_path.stem / "auto" / f"{input_path.stem}.md"
                    if possible_path_auto.exists():
                        md_file = str(possible_path_auto)
                    else:
                        print("⏭️  Skipped PDF parsing. No markdown file found in state or filesystem.")
                        return
            print(f"⏭️  Skipping Step 1: Using existing markdown: {md_file}")

        # Step 2: Read Markdown
        processor = MarkdownProcessor()
        if Config.PIPELINE_STEPS.get('read_markdown'):
            if not blocks:  # Only read if not loaded from state
                print("▶️  Step 2: Reading Markdown...")
                text = processor.load_markdown(md_file)
                state['markdown_text'] = text
                state['last_completed_step'] = 'read_markdown'
                state_manager.save(state)
            else:
                print("⏭️  Skipping Step 2: Using cached data")
        else:
            print("⏭️  Skipping Step 2: Read Markdown")
            text = state.get('markdown_text') or processor.load_markdown(md_file)
        
        # Step 3: Parse Markdown
        if Config.PIPELINE_STEPS.get('parse_markdown'):
            if not blocks:
                print("▶️  Step 3: Parsing Markdown...")
                blocks = processor.parse(text)
                print(f"✅ Found {len(blocks)} blocks.")
                state['blocks'] = [{'type': b.type, 'content': b.content, 'original': b.original, 'translation': b.translation} for b in blocks]
                state['last_completed_step'] = 'parse_markdown'
                state_manager.save(state)
            else:
                print(f"⏭️  Skipping Step 3: Using {len(blocks)} blocks from state")
        else:
            print("⏭️  Skipping Step 3: Parse Markdown")
        
        # Step 4: Identify text blocks
        if Config.PIPELINE_STEPS.get('identify_text_blocks'):
            print("▶️  Step 4: Identifying text blocks...")
            text_blocks = [b for b in blocks if b.type == 'text']
            print(f"✅ Identified {len(text_blocks)} text blocks for translation.")
            state['text_block_count'] = len(text_blocks)
            state['last_completed_step'] = 'identify_text_blocks'
            state_manager.save(state)
        else:
            print("⏭️  Skipping Step 4: Identify text blocks")
        
        # Step 4.1: Load glossary
        glossary_path = None
        if Config.PIPELINE_STEPS.get('load_glossary'):
            print("▶️  Step 4.1: Loading glossary...")
            if Config.GLOSSARY_FILENAME:
                glossary_path = Path(Config.ASSETS_DIR) / Config.GLOSSARY_FILENAME
                if glossary_path.exists():
                    print(f"✅ Glossary loaded: {glossary_path}")
                    state['glossary_path'] = str(glossary_path)
                    state['last_completed_step'] = 'load_glossary'
                    state_manager.save(state)
                else:
                    print("⚠️  Glossary file not found")
                    glossary_path = None
            else:
                print("ℹ️  Glossary disabled in config")
                glossary_path = None
        else:
            print("⏭️  Skipping Step 4.1: Load glossary")
            glossary_path = state.get('glossary_path')

        # Step 5: Translate
        if Config.PIPELINE_STEPS.get('translate'):
            print("▶️  Step 5: Translating...")
            translator = Translator(str(glossary_path) if glossary_path else None)
            text_blocks = [b for b in blocks if b.type == 'text']
            print(f"   Translating {len(text_blocks)} text blocks...")
            
            tasks = [translator.translate(b.content) for b in text_blocks]
            translations = await tqdm_asyncio.gather(*tasks, desc="Translating", unit="block")
            
            state['translations'] = translations
            state['last_completed_step'] = 'translate'
            state_manager.save(state)
            print("✅ Translation complete.")
        else:
            print("⏭️  Skipping Step 5: Translation")
            translations = state.get('translations', [])
        
        # Step 6: Merge translations
        if Config.PIPELINE_STEPS.get('merge_translations'):
            print("▶️  Step 6: Merging translations...")
            processor.inject_translations(blocks, translations)
            print("✅ Translations merged into blocks.")
            
            # Save updated blocks with translations
            state['blocks'] = [{'type': b.type, 'content': b.content, 'original': b.original, 'translation': b.translation} for b in blocks]
            state['last_completed_step'] = 'merge_translations'
            state_manager.save(state)
        else:
            print("⏭️  Skipping Step 6: Merge translations")

        # Step 7: Reconstruct bilingual markdown
        if Config.PIPELINE_STEPS.get('reconstruct_markdown'):
            print("▶️  Step 7: Reconstructing bilingual Markdown...")
            
            # Reconstruct bilingual markdown
            bilingual_text = processor.reconstruct(blocks, bilingual=True)
            
            # Save bilingual markdown
            output_dir = Path(md_file).parent
            bilingual_md_path = output_dir / f"{Path(md_file).stem}_bilingual.md"
            with open(bilingual_md_path, 'w', encoding='utf-8') as f:
                f.write(bilingual_text)
            print(f"✅ Bilingual Markdown saved to: {bilingual_md_path}")
            
            state['bilingual_md_path'] = str(bilingual_md_path)
            state['last_completed_step'] = 'reconstruct_markdown'
            state_manager.save(state)
        else:
            print("⏭️  Skipping Step 7: Markdown reconstruction")
            bilingual_md_path = state.get('bilingual_md_path')

        # Step 8: Generate Output
        if Config.PIPELINE_STEPS.get('generate_output'):
            print("▶️  Step 8: Generating output document...")
            
            if not bilingual_md_path:
                bilingual_md_path = state.get('bilingual_md_path')
            
            if not bilingual_md_path or not Path(bilingual_md_path).exists():
                print("❌ Error: Bilingual markdown not found. Run steps 0-7 first.")
                return
            
            output_dir = Path(bilingual_md_path).parent
            
            if Config.OUTPUT_FORMAT == 'pdf':
                print(f"📄 Generating PDF (Engine: xhtml2pdf)...")
                pdf_gen = PDFGenerator()
                pdf_path = output_dir / f"{Path(md_file).stem}_bilingual.pdf"
                try:
                    pdf_gen.generate(str(bilingual_md_path), str(pdf_path), title=input_path.stem)
                    print(f"✅ PDF generated successfully: {pdf_path}")
                    state['pdf_path'] = str(pdf_path)
                    state['last_completed_step'] = 'generate_output'
                    state_manager.save(state)
                except Exception as e:
                    print(f"❌ PDF generation failed: {e}")
                    raise e
            else:
                print(f"📚 Generating ePUB...")
                epub_gen = EpubGenerator()
                epub_path = output_dir / f"{Path(md_file).stem}_bilingual.epub"
                
                # Use cover image from state if available, otherwise try default path
                epub_cover_image = state.get('cover_image')
                if not epub_cover_image or not Path(epub_cover_image).exists():
                    epub_cover_image = output_dir / f"{Path(md_file).stem}_bilingual_cover.png"
                
                try:
                    epub_gen.generate(str(bilingual_md_path), str(epub_path), str(epub_cover_image), title=input_path.stem)
                    print(f"✅ ePUB generated successfully: {epub_path}")
                    
                    state['epub_path'] = str(epub_path)
                    state['last_completed_step'] = 'generate_output'
                    state_manager.save(state)
                except Exception as e:
                    print(f"❌ ePUB generation failed: {e}")
                    raise e
        else:
            print("⏭️  Skipping Step 8: Output generation")
        
        print("\n🎉 Pipeline completed!")
        print(f"📊 Last completed step: {state.get('last_completed_step', 'none')}") 
        print(f"📝 Log file: {log_file}")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise e # Re-raise for batch processor to catch if needed, though we catch above too. 
        # Actually, for batch processor, we want to know if it failed.
    finally:
        # Restore original stdout and close logger
        sys.stdout = original_stdout
        logger.close()
        print(f"\n📝 Log saved to: {log_file}")

async def main():
    parser = argparse.ArgumentParser(description="Bilingual ePUB Maker")
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output", help="Output directory (overrides config)")
    parser.add_argument("--preset", default="all", choices=list(Config.PIPELINE_PRESETS.keys()), help="Pipeline preset to run")
    parser.add_argument("--steps", help="Specific steps to run (e.g., '0-4' or '5-8')")
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    parser.add_argument("--check", action="store_true", help="Check completed steps from state file")
    parser.add_argument("--state-file", help="Path to state file (default: {output_dir}/pipeline_state.json")
    parser.add_argument("--format", choices=['epub', 'pdf'], default='epub', help="Output format (epub or pdf)")
    
    args = parser.parse_args()

    await process_single_file(
        input_file=args.input_file,
        output_dir=args.output,
        preset=args.preset,
        steps=args.steps,
        resume=args.resume,
        check=args.check,
        state_file=args.state_file,
        output_format=args.format
    )

if __name__ == "__main__":
    asyncio.run(main())

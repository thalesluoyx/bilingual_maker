import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EpubGenerator:
    def __init__(self):
        pass

    def generate(self, markdown_path: str, output_path: str, cover_image: str = None, title: str = "Bilingual Book") -> str:
        """
        Convert Markdown to ePUB using Pandoc.
        """
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)
        
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
            
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        subtitle_text = "Empowered by AI, supported by ThalesLuo"
        cmd = [
            "pandoc",
            str(markdown_path),
            "-o", str(output_path),
            "--toc",
            "--standalone",
            "--metadata", f"title={title}",
            "--metadata", f"subtitle={subtitle_text}", 
            "--resource-path", str(markdown_path.parent) # Ensure images are found
        ]
        
        if cover_image and Path(cover_image).exists():
            cmd.extend(["--epub-cover-image", str(cover_image)])
            
        logger.info(f"Generating ePUB: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"ePUB generated successfully: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc failed: {e.stderr}")
            raise RuntimeError(f"ePUB generation failed: {e.stderr}")

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 2:
        gen = EpubGenerator()
        gen.generate(sys.argv[1], sys.argv[2])

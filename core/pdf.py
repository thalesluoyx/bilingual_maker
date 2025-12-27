import subprocess
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        pass

    def sanitize_markdown(self, markdown_path: Path) -> Path:
        """
        Sanitizes Markdown content by wrapping raw HTML/XML code snippets in code blocks.
        Returns the path to the sanitized temporary file.
        """
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Indicators that a line is definitely code
        code_indicators = [
            r'<\s*%',          # JSP start
            r'%\s*>',          # JSP end
            r'=\s*\$',         # Malformed attribute =$
            r'width\s*\$',     # Malformed width
            r'align\s*\$',     # Malformed align
            r'valign\s*\$',    # Malformed valign
            r'<corepatterns:', # Custom tag
            r'</corepatterns:',
            r'<region:',       # Custom tag
            r'</region:',
            r'varepsilon',     # Math artifact in tag
            r'cdot',           # Math artifact
            r'^\s*\}\s*$',     # Closing brace on its own line
            r'^\s*while\s*\(', # Java while loop
            r'\\mathbf',       # LaTeX math artifact
            r'\\eta',          # LaTeX math artifact
            r'\\phantom',      # LaTeX math artifact
            r'public\s+static\s+final', # Java constant
        ]
        
        # Indicators that a line is likely code (standard HTML tags)
        html_tags = [
            r'^\s*<html', r'^\s*</html',
            r'^\s*<head', r'^\s*</head',
            r'^\s*<body', r'^\s*</body',
            r'^\s*<table', r'^\s*</table',
            r'^\s*<tr', r'^\s*</tr',
            r'^\s*<td', r'^\s*</td',
            r'^\s*<th', r'^\s*</th',
            r'^\s*<h\d', r'^\s*</h\d',
            r'^\s*<center', r'^\s*</center',
        ]

        def is_definite_code(line):
            return any(re.search(ind, line) for ind in code_indicators)

        def is_likely_code(line):
            return any(re.search(tag, line, re.IGNORECASE) for tag in html_tags)

        lines = content.split('\n')
        
        # First pass: mark lines as code or not
        is_code = [False] * len(lines)
        for i, line in enumerate(lines):
            if is_definite_code(line):
                is_code[i] = True
        
        # Second pass: expand code blocks to include adjacent "likely code" lines
        # Expand up
        for i in range(len(lines)):
            if is_code[i]:
                # Look back
                j = i - 1
                while j >= 0:
                    if not lines[j].strip(): # Skip blank lines
                        j -= 1
                        continue
                    if is_likely_code(lines[j]) and not is_code[j]:
                        is_code[j] = True
                        j -= 1
                    else:
                        break
                
                # Look forward
                j = i + 1
                while j < len(lines):
                    if not lines[j].strip(): # Skip blank lines
                        j += 1
                        continue
                    if is_likely_code(lines[j]) and not is_code[j]:
                        is_code[j] = True
                        j += 1
                    else:
                        break
                    
        # Third pass: Generate output with code fences
        new_lines = []
        i = 0
        blocks_created = 0
        while i < len(lines):
            if is_code[i]:
                blocks_created += 1
                new_lines.append("```html")
                while i < len(lines) and is_code[i]:
                    new_lines.append(lines[i])
                    i += 1
                new_lines.append("```")
            else:
                new_lines.append(lines[i])
                i += 1
        
        content = '\n'.join(new_lines)
        
        logger.info(f"Sanitized Markdown: Created {blocks_created} code blocks wrapping malformed HTML.")

        # Write to temp file
        sanitized_path = markdown_path.with_name(markdown_path.stem + "_sanitized.md")
        with open(sanitized_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return sanitized_path

    def generate(self, markdown_path: str, output_path: str, title: str = "Bilingual Book") -> str:
        """
        Convert Markdown to PDF using Pandoc + xelatex.
        Uses xeCJK for Chinese support.
        """
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)
        
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
            
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sanitize Markdown first (still useful for escaping raw HTML/JSP)
        sanitized_md_path = self.sanitize_markdown(markdown_path)
        
        # Convert Markdown directly to PDF using Pandoc + xelatex
        # We need to specify CJK main font for Chinese support
        cmd = [
            "pandoc",
            str(sanitized_md_path),
            "-o", str(output_path),
            "--toc",
            "--metadata", f"title={title}",
            "--resource-path", str(markdown_path.parent),
            "--pdf-engine=xelatex",
            "-V", "CJKmainfont=SimSun",
            "-V", "geometry:margin=2.5cm",
            "-V", "mainfont=Times New Roman",
            "--variable", "urlcolor=blue",
            "--variable", "linkcolor=blue"
        ]
        
        logger.info(f"Generating PDF with command: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"PDF generated successfully: {output_path}")
            
            # Clean up temp file
            if sanitized_md_path.exists() and sanitized_md_path != markdown_path:
                sanitized_md_path.unlink()
                
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc failed: {e.stderr}")
            raise RuntimeError(f"PDF generation failed: {e.stderr}")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise RuntimeError(f"PDF generation failed: {e}")

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 2:
        gen = PDFGenerator()
        gen.generate(sys.argv[1], sys.argv[2])

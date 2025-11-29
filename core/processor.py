import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ContentBlock:
    type: str  # 'text', 'code', 'image', 'formula', 'header', 'separator'
    content: str
    original: str  # The original markdown text
    translation: str = None
    metadata: Dict[str, Any] = None

class MarkdownProcessor:
    def __init__(self):
        pass

    def load_markdown(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def parse(self, markdown_text: str) -> List[ContentBlock]:
        """
        Parse markdown text into a list of ContentBlocks.
        """
        blocks = []
        lines = markdown_text.split('\n')
        
        current_content = []
        
        # Regex patterns
        code_block_pattern = re.compile(r'^```')
        header_pattern = re.compile(r'^#+\s')
        image_pattern = re.compile(r'!\[.*?\]\(.*?\)')
        math_block_pattern = re.compile(r'^\$\$')
        
        in_code_block = False
        in_math_block = False
        
        for line in lines:
            # Handle Code Blocks
            if code_block_pattern.match(line):
                if in_code_block:
                    # End of code block
                    current_content.append(line)
                    blocks.append(ContentBlock('code', '\n'.join(current_content), '\n'.join(current_content)))
                    current_content = []
                    in_code_block = False
                    continue
                else:
                    # Start of code block
                    if current_content:
                        self._save_text_block(blocks, current_content)
                        current_content = []
                    in_code_block = True
                    current_content.append(line)
                    continue
            
            if in_code_block:
                current_content.append(line)
                continue

            # Handle Math Blocks ($$)
            if math_block_pattern.match(line):
                if in_math_block:
                    # End of math block
                    current_content.append(line)
                    blocks.append(ContentBlock('formula', '\n'.join(current_content), '\n'.join(current_content)))
                    current_content = []
                    in_math_block = False
                    continue
                else:
                    # Start of math block
                    if current_content:
                        self._save_text_block(blocks, current_content)
                        current_content = []
                    in_math_block = True
                    current_content.append(line)
                    continue
            
            if in_math_block:
                current_content.append(line)
                continue

            # Handle Headers
            if header_pattern.match(line):
                if current_content:
                    self._save_text_block(blocks, current_content)
                    current_content = []
                blocks.append(ContentBlock('header', line, line))
                continue

            # Handle Images
            if image_pattern.match(line):
                if current_content:
                    self._save_text_block(blocks, current_content)
                    current_content = []
                blocks.append(ContentBlock('image', line, line))
                continue

            # Regular Text
            if line.strip() == "":
                if current_content:
                    self._save_text_block(blocks, current_content)
                    current_content = []
                blocks.append(ContentBlock('separator', '', '\n'))
            else:
                current_content.append(line)
        
        # Flush remaining content
        if current_content:
            self._save_text_block(blocks, current_content)
            
        return blocks

    def _save_text_block(self, blocks, content_lines):
        text = '\n'.join(content_lines)
        if text.strip():
            blocks.append(ContentBlock('text', text, text))

    def inject_translations(self, blocks: List[ContentBlock], translations: List[str]):
        """
        Inject translations into text blocks.
        """
        text_blocks = [b for b in blocks if b.type == 'text']
        
        # We assume the translations list corresponds exactly to the text blocks
        # If lengths mismatch, we try to map as many as possible
        for i, block in enumerate(text_blocks):
            if i < len(translations):
                block.translation = translations[i]

    def reconstruct(self, blocks: List[ContentBlock], bilingual: bool = False) -> str:
        """
        Reconstruct markdown from blocks.
        """
        output = []
        for block in blocks:
            if block.type == 'text' and bilingual and block.translation:
                # Bilingual format: Original \n\n Translation
                output.append(block.content)
                output.append("\n\n")
                output.append(block.translation)
                output.append("\n")
            elif block.type == 'separator':
                output.append(block.original)
            else:
                output.append(block.original)
                output.append("\n")
        
        return "".join(output)

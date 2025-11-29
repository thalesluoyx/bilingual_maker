import pytest
from core.processor import MarkdownProcessor, ContentBlock

@pytest.fixture
def processor():
    return MarkdownProcessor()

def test_parse_simple_text(processor):
    text = "Hello World"
    blocks = processor.parse(text)
    assert len(blocks) == 1
    assert blocks[0].type == 'text'
    assert blocks[0].content == "Hello World"

def test_parse_code_block(processor):
    text = """
```python
print("Hello")
```
"""
    blocks = processor.parse(text.strip())
    assert len(blocks) == 1
    assert blocks[0].type == 'code'
    assert "print" in blocks[0].content

def test_parse_mixed_content(processor):
    text = """# Header
Paragraph 1.

![Image](img.png)

Paragraph 2.
"""
    blocks = processor.parse(text)
    # Header, Separator, Text, Separator, Image, Separator, Text, Separator (maybe)
    # Let's check types
    types = [b.type for b in blocks]
    assert 'header' in types
    assert 'text' in types
    assert 'image' in types

def test_reconstruct_bilingual(processor):
    blocks = [
        ContentBlock(type='text', content='Hello', original='Hello', translation='你好'),
        ContentBlock(type='separator', content='', original='\n')
    ]
    output = processor.reconstruct(blocks, bilingual=True)
    assert "Hello" in output
    assert "你好" in output

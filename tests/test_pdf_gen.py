import pytest
from pathlib import Path
from core.pdf import PDFGenerator
from pypdf import PdfReader

def test_pdf_generation(tmp_path):
    """Test PDF generation with xhtml2pdf."""
    # Create a dummy markdown file
    md_content = """
# Test Title

This is a test paragraph with some **bold** and *italic* text.

## Section 2

- Item 1
- Item 2

### Chinese Support

这是一个测试段落，包含中文。
    """
    
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")
    
    output_pdf = tmp_path / "test.pdf"
    
    generator = PDFGenerator()
    
    # This should succeed if fixed, or fail with the CSS error if not
    try:
        result_path = generator.generate(str(md_file), str(output_pdf), title="Test Book")
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0
        print(f"PDF generated successfully at: {result_path}")
        
        # Verify Chinese content
        reader = PdfReader(result_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            
        print(f"Extracted text: {text}")
        assert "这是一个测试段落" in text, "Chinese characters not found in PDF"
        
    except Exception as e:
        pytest.fail(f"PDF generation failed: {e}")

if __name__ == "__main__":
    # Allow running directly
    import sys
    import shutil
    
    # Create a temp dir for manual run
    test_dir = Path("temp_test_pdf")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    try:
        test_pdf_generation(test_dir)
        print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")

import pytest
from unittest.mock import patch
from core.epub import EpubGenerator

def test_generate_epub_success():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        generator = EpubGenerator()
        # Create dummy files for path validation
        with patch('pathlib.Path.exists', return_value=True):
            output = generator.generate("input.md", "output.epub")
            assert output == "output.epub"
            mock_run.assert_called_once()

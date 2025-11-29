import pytest
import asyncio
from core.translator import Translator
from core.glossary import GlossaryLoader

def test_glossary_loading():
    """Test that glossary loads correctly."""
    glossary = GlossaryLoader("assets/astrodict241020_ec.txt")
    assert len(glossary.glossary) > 0
    
    # Test case-insensitive lookup for redshift
    assert glossary.get_translation("redshift") == "红移"
    assert glossary.get_translation("RedShift") == "红移"
    assert glossary.get_translation("Redshift") == "红移"
    
    # Test Black Hole
    translation = glossary.get_translation("Black Hole")
    assert translation is not None
    assert "黑洞" in translation

def test_glossary_relevant_terms():
    """Test extraction of relevant terms from text."""
    glossary = GlossaryLoader("assets/astrodict241020_ec.txt")
    
    text = "The redshift of the galaxy indicates it is moving away. Black holes are fascinating."
    relevant = glossary.get_relevant_terms(text)
    
    assert len(relevant) > 0
    # Should find redshift and black hole
    assert any("redshift" in term.lower() for term in relevant.keys())

@pytest.mark.asyncio
async def test_translator_with_glossary():
    """Test translator uses glossary correctly."""
    translator = Translator("assets/astrodict241020_ec.txt")
    
    # Text containing astronomy terms
    text = "The redshift of distant galaxies provides evidence for the expanding universe."
    result = await translator.translate(text, use_glossary=True)
    
    print(f"\nInput: {text}")
    print(f"Output: {result}")
    
    # Check that translation contains the correct term
    assert result is not None
    assert len(result) > 0
    assert "红移" in result  # Should use glossary term for redshift

@pytest.mark.asyncio
async def test_translator_without_glossary():
    """Test translator works without glossary."""
    translator = Translator()  # No glossary
    
    text = "Hello, World!"
    result = await translator.translate(text, use_glossary=False)
    
    assert result is not None
    assert len(result) > 0

if __name__ == "__main__":
    asyncio.run(test_translator_with_glossary())

import pytest
import asyncio
from core.translator import Translator

@pytest.mark.asyncio
async def test_llm_connectivity():
    """
    Test actual connectivity to the LLM API.
    This test makes a real network request.
    """
    print("\nTesting LLM Connectivity...")
    translator = Translator()
    
    # Simple hello world translation
    text = "Hello, World!"
    print(f"Input: {text}")
    
    try:
        result = await translator.translate(text)
        print(f"Output: {result}")
        
        assert result is not None
        assert len(result) > 0
        assert "Error" not in result
        
        # Basic check if it contains Chinese characters (assuming translation to Chinese)
        # But the prompt might not strictly enforce Chinese if the model is chatty, 
        # though system prompt says "Translate... into professional Chinese".
        # Let's just check it's not empty and not an error.
        
    except Exception as e:
        pytest.fail(f"LLM Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_connectivity())

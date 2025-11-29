import pytest
from unittest.mock import AsyncMock, patch
from core.translator import Translator

@pytest.mark.asyncio
async def test_translate_success():
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '你好'}}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        translator = Translator()
        result = await translator.translate("Hello")
        assert result == "你好"

@pytest.mark.asyncio
async def test_translate_empty():
    translator = Translator()
    result = await translator.translate("")
    assert result == ""

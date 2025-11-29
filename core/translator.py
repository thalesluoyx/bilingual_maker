import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from config import Config
from core.glossary import GlossaryLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    def __init__(self, glossary_path: str = None):
        self.semaphore = asyncio.Semaphore(Config.MAX_CONCURRENCY)
        self.headers = Config.get_headers()
        self.base_url = Config.BASE_URL
        
        # Load glossary if provided
        self.glossary = None
        if glossary_path:
            self.glossary = GlossaryLoader(glossary_path)
            logger.info(f"Loaded glossary with {len(self.glossary.glossary)} terms")
        if not self.base_url.endswith('/v1'):
             # Ensure base_url ends with /v1 if needed, or just trust config
             # OpenAI compatible usually is .../v1
             pass

    async def translate(self, text: str, use_glossary: bool = True) -> str:
        """
        Translate text using the configured LLM API.
        """
        if not text.strip():
            return ""

        async with self.semaphore:
            return await self._make_request(text, use_glossary)

    async def _make_request(self, text: str, use_glossary: bool = True) -> str:
        # Extract relevant glossary terms if available
        specific_glossary = None
        if use_glossary and self.glossary:
            relevant_terms = self.glossary.get_relevant_terms(text, max_terms=30)
            if relevant_terms:
                specific_glossary = self.glossary.format_for_prompt(relevant_terms)
        
        payload = Config.get_payload(text, specific_glossary)
        # Construct URL: assume BASE_URL is the root or the full path?
        # Config says "Base URL + API Key". Usually BASE_URL is like "https://api.openai.com/v1"
        # So we append "/chat/completions"
        url = f"{self.base_url}/chat/completions"
        
        for attempt in range(Config.RETRY_ATTEMPTS):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=self.headers, json=payload, timeout=Config.TIMEOUT_SECONDS) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'choices' in data and len(data['choices']) > 0:
                                return data['choices'][0]['message']['content'].strip()
                            else:
                                logger.error(f"Unexpected response format: {data}")
                                return "[Translation Error: Invalid Response]"
                        elif response.status == 429:
                            wait_time = 2 ** attempt
                            logger.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                        else:
                            error_text = await response.text()
                            logger.error(f"API Error {response.status}: {error_text}")
                            if 400 <= response.status < 500:
                                return f"[Translation Error: {response.status}]"
                            # Retry on 5xx
                            await asyncio.sleep(1)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Request failed: {e}")
                await asyncio.sleep(1)
        
        return "[Translation Failed]"

if __name__ == "__main__":
    # Test
    async def test():
        translator = Translator()
        result = await translator.translate("The quick brown fox jumps over the lazy dog.")
        print(f"Result: {result}")

    asyncio.run(test())

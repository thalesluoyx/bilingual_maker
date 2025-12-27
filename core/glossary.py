import re
from pathlib import Path
from typing import Dict, List

class GlossaryLoader:
    def __init__(self, glossary_path: str):
        self.glossary_path = Path(glossary_path)
        self.glossary = {}
        self.load()
    
    def load(self):
        """Load glossary from tab-separated file."""
        if not self.glossary_path.exists():
            print(f"Warning: Glossary file not found: {self.glossary_path}")
            return
        
        with open(self.glossary_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '\t' not in line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    english = parts[0].strip()
                    chinese = parts[1].strip()
                    
                    # Store the term (case-insensitive key)
                    key = english.lower()
                    if key not in self.glossary:
                        self.glossary[key] = {
                            'original': english,
                            'translation': chinese,
                            'variants': [english]
                        }
                    else:
                        # Add variant if not already present
                        if english not in self.glossary[key]['variants']:
                            self.glossary[key]['variants'].append(english)
    
    def get_translation(self, term: str) -> str:
        """Get translation for a term (case-insensitive)."""
        key = term.lower()
        if key in self.glossary:
            return self.glossary[key]['translation']
        return None
    
    def get_relevant_terms(self, text: str, max_terms: int = 50) -> Dict[str, str]:
        """
        Extract relevant glossary terms found in the text.
        Returns a dict of {english_term: chinese_translation}.
        """
        relevant = {}
        text_lower = text.lower()
        
        for key, data in self.glossary.items():
            # Check if any variant appears in the text
            for variant in data['variants']:
                # Use word boundary matching for better accuracy
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    relevant[data['original']] = data['translation']
                    break
            
            if len(relevant) >= max_terms:
                break
        
        return relevant
    
    def format_for_prompt(self, terms: Dict[str, str]) -> str:
        """Format glossary terms for inclusion in LLM prompt."""
        if not terms:
            return ""
        
        lines = []
        for eng, chn in terms.items():
            lines.append(f"    - {eng} → {chn}")
        
        return "\n".join(lines)

if __name__ == "__main__":
    from config import Config
    # Test
    filename = Config.GLOSSARY_FILENAME or "astrodict241020_ec.txt"
    glossary_path = Path(Config.ASSETS_DIR) / filename
    loader = GlossaryLoader(str(glossary_path))
    print(f"Loaded {len(loader.glossary)} terms")
    
    # Test case-insensitive lookup
    test_terms = ["redshift", "RedShift", "red shift", "Black Hole"]
    for term in test_terms:
        translation = loader.get_translation(term)
        print(f"{term} → {translation}")

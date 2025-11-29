import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class PipelineState:
    def __init__(self, state_file: str = None):
        self.state_file = Path(state_file) if state_file else None
        self.data = {}
    
    def save(self, data: Dict[str, Any]):
        """Save pipeline state to JSON file."""
        if not self.state_file:
            return
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 State saved to: {self.state_file}")
    
    def load(self) -> Dict[str, Any]:
        """Load pipeline state from JSON file."""
        if not self.state_file or not self.state_file.exists():
            return {}
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 State loaded from: {self.state_file}")
        print(f"   Last updated: {data.get('timestamp', 'unknown')}")
        print(f"   Last completed step: {data.get('last_completed_step', 'none')}")
        
        return data
    
    def exists(self) -> bool:
        """Check if state file exists."""
        return self.state_file and self.state_file.exists()

    def get_completed_steps(self) -> List[str]:
        """Get list of completed steps based on state."""
        if not self.exists():
            return []
        
        data = self.load()
        last_step = data.get('last_completed_step')
        if not last_step:
            return []
            
        # Define step order
        steps = [
            'prepare_paths',
            'pdf_to_markdown',
            'read_markdown',
            'parse_markdown',
            'identify_text_blocks',
            'load_glossary',
            'translate',
            'merge_translations',
            'reconstruct_markdown',
            'generate_epub'
        ]
        
        try:
            idx = steps.index(last_step)
            return steps[:idx+1]
        except ValueError:
            return []

if __name__ == "__main__":
    # Test
    state = PipelineState("test_state.json")
    state.save({
        'input_file': 'test.pdf',
        'md_file': 'test.md',
        'last_completed_step': 'parse_markdown'
    })
    
    loaded = state.load()
    print(loaded)

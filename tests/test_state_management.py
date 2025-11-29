import pytest
import json
from pathlib import Path
from core.state import PipelineState

def test_state_save_and_load(tmp_path):
    """Test saving and loading state."""
    state_file = tmp_path / "test_state.json"
    state_manager = PipelineState(str(state_file))
    
    # Save state
    test_data = {
        'input_file': 'test.pdf',
        'md_file': 'test.md',
        'last_completed_step': 'parse_markdown'
    }
    state_manager.save(test_data)
    
    # Verify file exists
    assert state_file.exists()
    
    # Load state
    loaded_data = state_manager.load()
    assert loaded_data['input_file'] == 'test.pdf'
    assert loaded_data['md_file'] == 'test.md'
    assert loaded_data['last_completed_step'] == 'parse_markdown'
    assert 'timestamp' in loaded_data

def test_state_file_not_exists():
    """Test loading when state file doesn't exist."""
    state_manager = PipelineState("nonexistent.json")
    loaded_data = state_manager.load()
    assert loaded_data == {}

def test_state_exists_check(tmp_path):
    """Test state file existence check."""
    state_file = tmp_path / "test_state.json"
    state_manager = PipelineState(str(state_file))
    
    # Should not exist initially
    assert not state_manager.exists()
    
    # Save something
    state_manager.save({'test': 'data'})
    
    # Should exist now
    assert state_manager.exists()

def test_state_persistence_with_blocks(tmp_path):
    """Test saving and loading blocks data."""
    state_file = tmp_path / "test_state.json"
    state_manager = PipelineState(str(state_file))
    
    # Create test blocks
    blocks_data = [
        {'type': 'text', 'content': 'Hello', 'original': 'Hello', 'translation': None},
        {'type': 'code', 'content': 'print()', 'original': 'print()', 'translation': None}
    ]
    
    test_data = {
        'blocks': blocks_data,
        'last_completed_step': 'parse_markdown'
    }
    
    state_manager.save(test_data)
    loaded_data = state_manager.load()
    
    assert len(loaded_data['blocks']) == 2
    assert loaded_data['blocks'][0]['type'] == 'text'
    assert loaded_data['blocks'][1]['type'] == 'code'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

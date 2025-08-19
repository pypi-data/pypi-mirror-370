"""Test emoji mapping functionality."""

import pytest
import tempfile
import json
import os
from emojify_python import (
    add_custom_mapping, remove_custom_mapping,
    update_default_mapping, remove_default_mapping,
    get_module_for_emoji, get_emoji_for_module,
    get_all_mappings, reset_custom_mappings,
    list_mappings, save_custom_mappings, load_custom_mappings,
    search_mapping, DEFAULT_MAPPINGS
)

class TestMappings:
    """Test emoji mapping management."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_custom_mappings()
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_custom_mappings()
    
    def test_default_mappings(self):
        """Test that default mappings exist."""
        assert len(DEFAULT_MAPPINGS) > 0
        assert '🐼' in DEFAULT_MAPPINGS
        assert DEFAULT_MAPPINGS['🐼'] == 'pandas'
    
    def test_get_module_for_emoji(self):
        """Test getting module name for emoji."""
        assert get_module_for_emoji('🐼') == 'pandas'
        assert get_module_for_emoji('📊') == 'matplotlib'
        assert get_module_for_emoji('unknown_emoji') == 'unknown_emoji'
    
    def test_get_emoji_for_module(self):
        """Test getting emoji for module name."""
        assert get_emoji_for_module('pandas') == '🐼'
        assert get_emoji_for_module('matplotlib') == '📊'
        assert get_emoji_for_module('unknown_module') == 'unknown_module'
    
    def test_add_custom_mapping(self):
        """Test adding custom mappings."""
        add_custom_mapping('🎮', 'pygame')
        assert get_module_for_emoji('🎮') == 'pygame'
        
        # Custom mappings should override defaults
        add_custom_mapping('🐼', 'custom_pandas')
        assert get_module_for_emoji('🐼') == 'custom_pandas'
    
    def test_remove_custom_mapping(self):
        """Test removing custom mappings."""
        # Use an emoji that's not in DEFAULT_MAPPINGS
        add_custom_mapping('🦄', 'unicorn_module')
        assert get_module_for_emoji('🦄') == 'unicorn_module'
        
        remove_custom_mapping('🦄')
        assert get_module_for_emoji('🦄') == '🦄'
    
    def test_update_default_mapping(self):
        """Test updating default mappings."""
        original = DEFAULT_MAPPINGS.get('🆕', None)
        
        update_default_mapping('🆕', 'new_module')
        assert DEFAULT_MAPPINGS['🆕'] == 'new_module'
        assert get_module_for_emoji('🆕') == 'new_module'
        
        # Clean up
        if original is None and '🆕' in DEFAULT_MAPPINGS:
            del DEFAULT_MAPPINGS['🆕']
    
    def test_remove_default_mapping(self):
        """Test removing default mappings."""
        # Add a test mapping
        update_default_mapping('🆕', 'test_module')
        assert '🆕' in DEFAULT_MAPPINGS
        
        # Remove it
        assert remove_default_mapping('🆕') == True
        assert '🆕' not in DEFAULT_MAPPINGS
        
        # Try removing non-existent
        assert remove_default_mapping('🆕') == False
    
    def test_list_mappings(self):
        """Test listing mappings."""
        add_custom_mapping('🎮', 'pygame')
        
        mappings = list_mappings()
        assert 'default' in mappings
        assert 'custom' in mappings
        assert '🐼' in mappings['default']
        assert '🎮' in mappings['custom']
        
        # Test filtering
        mappings = list_mappings(show_custom=False)
        assert 'default' in mappings
        assert 'custom' not in mappings
    
    def test_save_load_custom_mappings(self):
        """Test saving and loading custom mappings."""
        # Add some custom mappings (use emojis not in DEFAULT_MAPPINGS)
        add_custom_mapping('🦄', 'unicorn_module')
        add_custom_mapping('🌮', 'taco_module')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            save_custom_mappings(temp_file)
            
            # Reset and verify they're gone
            reset_custom_mappings()
            assert get_module_for_emoji('🦄') == '🦄'
            
            # Load them back
            load_custom_mappings(temp_file)
            assert get_module_for_emoji('🦄') == 'unicorn_module'
            assert get_module_for_emoji('🌮') == 'taco_module'
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_search_mapping(self):
        """Test searching for mappings."""
        # Search by module name
        results = search_mapping('pandas')
        assert '🐼' in results
        assert results['🐼'] == 'pandas'
        
        # Search by emoji
        results = search_mapping('🐼')
        assert '🐼' in results
        
        # Search partial match
        results = search_mapping('json')
        assert '📦' in results
        
        # Add custom and search
        add_custom_mapping('🎮', 'pygame')
        results = search_mapping('game')
        assert '🎮' in results
    
    def test_get_all_mappings(self):
        """Test getting all mappings."""
        add_custom_mapping('🎮', 'pygame')
        
        all_mappings = get_all_mappings()
        assert '🐼' in all_mappings  # Default
        assert '🎮' in all_mappings  # Custom
        assert all_mappings['🐼'] == 'pandas'
        assert all_mappings['🎮'] == 'pygame'
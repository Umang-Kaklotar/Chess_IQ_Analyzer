"""
Configuration Module

Loads and manages application configuration from config files.
Provides default values and configuration overrides.
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "ui": {
        "screen_size": (1200, 800),
        "theme": "default",
        "show_legal_moves": True,
        "show_last_move": True,
        "show_coordinates": True,
        "animation_speed": 5
    },
    "game": {
        "default_time_control": "10+5",
        "default_ai_difficulty": 3,
        "auto_queen_promotion": False,
        "auto_save_games": True
    },
    "analysis": {
        "engine_depth": 18,
        "save_analysis": True,
        "critical_position_threshold": 200
    },
    "sound": {
        "enabled": True,
        "volume": 0.7
    },
    "paths": {
        "game_history": "data/game_history.json",
        "player_stats": "data/player_stats.json",
        "logs": "logs"
    }
}

# Config file path
CONFIG_FILE = "config.json"

def load_config(config_file: str = CONFIG_FILE) -> Dict[str, Any]:
    """
    Load configuration from file, falling back to defaults.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dict containing configuration values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Try to load config from file
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                
            # Update default config with file values
            _update_config_recursive(config, file_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
    
    return config

def _update_config_recursive(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> None:
    """
    Recursively update base_config with values from override_config.
    
    Args:
        base_config: Base configuration to update
        override_config: Configuration with override values
    """
    for key, value in override_config.items():
        if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
            _update_config_recursive(base_config[key], value)
        else:
            base_config[key] = value

def save_config(config: Dict[str, Any], config_file: str = CONFIG_FILE) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration to save
        config_file: Path to save configuration to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving config file: {e}")
        return False

def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value by dot-separated path.
    
    Args:
        key_path: Dot-separated path to configuration value (e.g., "ui.theme")
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    config = load_config()
    keys = key_path.split('.')
    
    # Navigate through the config dictionary
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

def update_config_value(key_path: str, value: Any) -> bool:
    """
    Update a configuration value by dot-separated path.
    
    Args:
        key_path: Dot-separated path to configuration value (e.g., "ui.theme")
        value: New value to set
        
    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    keys = key_path.split('.')
    
    # Navigate to the parent of the target key
    current = config
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    # Set the value
    current[keys[-1]] = value
    
    # Save the updated config
    return save_config(config)

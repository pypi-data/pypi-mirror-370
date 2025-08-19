"""Configuration management for ATC"""

import json
import os
from pathlib import Path
from typing import Optional

from .models import DEFAULT_MODEL, get_full_model_name

def get_config_dir():
    """Get the configuration directory using XDG specification"""
    xdg_state_home = os.environ.get('XDG_STATE_HOME')
    if xdg_state_home:
        return Path(xdg_state_home) / 'atc'
    else:
        return Path.home() / '.local' / 'state' / 'atc'

def get_config_file():
    """Get the configuration file path"""
    return get_config_dir() / 'settings.json'

def load_config():
    """Load configuration from file"""
    config_file = get_config_file()
    
    if not config_file.exists():
        return {'default_model': DEFAULT_MODEL}
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {'default_model': DEFAULT_MODEL}

def save_config(config):
    """Save configuration to file"""
    config_file = get_config_file()
    config_dir = config_file.parent
    
    config_dir.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def get_default_model():
    """Get the default model from configuration"""
    config = load_config()
    return config.get('default_model', DEFAULT_MODEL)

def set_default_model(model_name):
    """Set the default model in configuration"""
    config = load_config()
    config['default_model'] = model_name
    save_config(config)
    return get_full_model_name(model_name)
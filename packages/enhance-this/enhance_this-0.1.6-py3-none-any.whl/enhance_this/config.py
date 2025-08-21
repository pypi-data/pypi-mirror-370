import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "default_temperature": 0.7,
    "default_style": "detailed",
    "ollama_host": "http://localhost:11434",
    "timeout": 30,
    "max_tokens": 2000,
    "auto_copy": True,
    "display_colors": True,
    "auto_download_model": True,
    "enhancement_templates": {},
}

def get_config_path(config_path_str: Optional[str] = None) -> Path:
    if config_path_str:
        return Path(config_path_str)
    return Path.home() / ".enhance-this" / "config.yaml"

def load_config(config_path_str: Optional[str] = None) -> Dict[str, Any]:
    config_path = get_config_path(config_path_str)
    if not config_path.exists():
        return DEFAULT_CONFIG
    
    try:
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
        
        config = DEFAULT_CONFIG.copy()
        if user_config:
            config.update(user_config)
        return config
    except (yaml.YAMLError, IOError):
        return DEFAULT_CONFIG

def ensure_config_dir_exists():
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

def create_default_config_if_not_exists():
    ensure_config_dir_exists()
    config_path = get_config_path()
    if not config_path.exists():
        config_to_write = DEFAULT_CONFIG.copy()
        # Example for user
        config_to_write['enhancement_templates'] = {
            'my_style': '/path/to/your/custom_template.txt'
        }
        with open(config_path, 'w') as f:
            yaml.dump(config_to_write, f, default_flow_style=False, sort_keys=False)

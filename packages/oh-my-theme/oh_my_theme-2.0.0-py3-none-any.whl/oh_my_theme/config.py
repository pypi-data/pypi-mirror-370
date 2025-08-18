"""
Configuration management for Oh My Theme.
Handles storage and retrieval of custom repositories and settings.
"""

import os
import json


CONFIG_DIR = os.path.expanduser("~/.config/oh-my-theme")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load_config():
    """Load configuration from file.
    
    Returns:
        dict: Configuration data with default values
    """
    default_config = {
        "custom_repositories": [],
        "settings": {
            "cache_expiry": 300,
            "max_cache_size": 50
        }
    }
    
    if not os.path.exists(CONFIG_FILE):
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Merge with defaults to ensure all keys exist
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
    except (json.JSONDecodeError, IOError):
        return default_config


def save_config(config):
    """Save configuration to file.
    
    Args:
        config (dict): Configuration data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def add_custom_repository(repo_url):
    """Add a custom repository to the configuration.
    
    Args:
        repo_url (str): The repository URL to add
        
    Returns:
        bool: True if added successfully, False if already exists
    """
    config = load_config()
    
    if repo_url not in config["custom_repositories"]:
        config["custom_repositories"].append(repo_url)
        return save_config(config)
    
    return False  # Already exists


def remove_custom_repository(repo_url):
    """Remove a custom repository from the configuration.
    
    Args:
        repo_url (str): The repository URL to remove
        
    Returns:
        bool: True if removed successfully, False if not found
    """
    config = load_config()
    
    if repo_url in config["custom_repositories"]:
        config["custom_repositories"].remove(repo_url)
        return save_config(config)
    
    return False  # Not found


def get_custom_repositories():
    """Get list of custom repositories.
    
    Returns:
        list: List of custom repository URLs
    """
    config = load_config()
    return config.get("custom_repositories", [])


def get_setting(key, default=None):
    """Get a configuration setting.
    
    Args:
        key (str): Setting key
        default: Default value if key not found
        
    Returns:
        Setting value or default
    """
    config = load_config()
    return config.get("settings", {}).get(key, default)


def set_setting(key, value):
    """Set a configuration setting.
    
    Args:
        key (str): Setting key
        value: Setting value
        
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_config()
    if "settings" not in config:
        config["settings"] = {}
    
    config["settings"][key] = value
    return save_config(config)
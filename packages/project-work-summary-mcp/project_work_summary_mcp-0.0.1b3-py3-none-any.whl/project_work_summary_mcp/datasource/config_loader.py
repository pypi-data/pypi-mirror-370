"""
Configuration Loader for MySQL Connection
Loads database configuration from environment variables or config file.
"""

import os
import json
from typing import Dict, Any

def load_mysql_config() -> Dict[str, Any]:
    """
    Load MySQL configuration from environment variables or default values.
    
    Returns:
        Dict[str, Any]: MySQL configuration dictionary
    """
    # Determine environment from environment variable
    env = os.getenv('ENV', 'test')  # Default to 'test' if not specified
    
    # Load configuration based on environment
    if env == 'prod':
        return _load_prod_config()
    else:  # Default to test environment
        return _load_test_config()

def _load_test_config() -> Dict[str, Any]:
    """Load test environment configuration."""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DATABASE', 'test_db'),
        'user': os.getenv('MYSQL_USER', 'test_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'test_password'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'autocommit': True,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }

def _load_prod_config() -> Dict[str, Any]:
    """Load production environment configuration."""
    return {
        'host': os.getenv('MYSQL_HOST', 'prod-server.example.com'),
        'database': os.getenv('MYSQL_DATABASE', 'prod_db'),
        'user': os.getenv('MYSQL_USER', 'prod_user'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'autocommit': True,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'ssl_disabled': True  # Disable SSL for production if needed
    }

def load_mysql_config_from_file(env: str = None) -> Dict[str, Any]:
    """
    Load MySQL configuration from a JSON file based on environment.
    
    Args:
        env (str): Environment ('test' or 'prod'). If None, uses ENV environment variable.
        
    Returns:
        Dict[str, Any]: MySQL configuration dictionary
    """
    if env is None:
        env = os.getenv('ENV', 'test')
    
    # Determine config file path based on environment
    if env == 'prod':
        file_path = 'config/mysql_prod_config.json'
    else:
        file_path = 'config/mysql_test_config.json'
    
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Return default config if file not found
        return load_mysql_config()
    except json.JSONDecodeError:
        # Return default config if file is invalid
        return load_mysql_config()
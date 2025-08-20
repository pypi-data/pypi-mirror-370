import os
import configparser
from typing import Dict, Any

def load_config(config_file: str = "tnz_mcp.ini") -> Dict[str, Any]:
    """Load configuration from environment or config file."""
    config = {"auth_token": None}
    
    # Check environment variable first
    config["auth_token"] = os.getenv("TNZ_AUTH_TOKEN")
    
    # Check config file if exists
    if not config["auth_token"] and os.path.exists(config_file):
        parser = configparser.ConfigParser()
        parser.read(config_file)
        if "TNZ" in parser and "AuthToken" in parser["TNZ"]:
            config["auth_token"] = parser["TNZ"]["AuthToken"]
    
    return config

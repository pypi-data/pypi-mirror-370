import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path.home() / '.antishlop'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)

def get_api_key():
    # Check environment variable first
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        return api_key
    
    # Check config file
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('api_key')
    
    return None

def set_api_key(api_key):
    ensure_config_dir()
    config = {}
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    config['api_key'] = api_key
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return True

def validate_api_key(api_key):
    if not api_key:
        return False
    if not api_key.startswith('sk-'):
        return False
    if len(api_key) < 20:
        return False
    return True
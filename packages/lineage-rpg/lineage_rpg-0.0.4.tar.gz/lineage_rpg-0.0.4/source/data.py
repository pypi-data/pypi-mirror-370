import os
import json
from lineage_rpg import schema

APP_NAME = "lineage_rpg"

if os.name == 'nt':  # Windows
    base_dir = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
else:  # macOS/Linux
    base_dir = os.path.expanduser("~/.local/share")

SAVE_DIR = os.path.join(base_dir, APP_NAME)
SAVE_FILE = os.path.join(SAVE_DIR, "player_data.json")

def load_save():
    if not os.path.exists(SAVE_FILE):
        return schema.DATA_SCHEMA.copy()

    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Save file is corrupted or unreadable. Starting fresh.")
        return schema.DATA_SCHEMA.copy()

    # Ensure all expected keys exist
    for key, value in schema.DATA_SCHEMA.items():
        data.setdefault(key, value)

    return data

def save_data(data):
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
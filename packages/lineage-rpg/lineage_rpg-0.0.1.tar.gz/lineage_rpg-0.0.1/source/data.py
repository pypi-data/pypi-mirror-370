import os
import json

from source import contants, schema

SAVE_FILE = os.path.expanduser(contants.SAVE_FILE_PATH)

def load_save():
    if not os.path.exists(SAVE_FILE):
        return schema.DATA_SCHEMA.copy()
    
    with open(SAVE_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Save file is corrupted. Starting fresh.")
            return schema.DATA_SCHEMA.copy()
    
    for key, value in schema.DATA_SCHEMA.items():
        data.setdefault(key, value)
    
    return data

def save_data(data):
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

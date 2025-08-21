import os
import json

from lineage import contants

SAVE_FILE = os.path.expanduser(contants.SAVE_FILE_PATH)

def load_save():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)
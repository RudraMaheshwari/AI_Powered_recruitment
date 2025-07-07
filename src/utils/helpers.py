"""
Helper functions for the recruitment assistant
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False

def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading from {filepath}: {e}")
        return {}

def append_to_json_list(data: Dict[str, Any], filepath: str, key: str = "items") -> bool:
    """Append data to a JSON list"""
    try:
        existing_data = load_json(filepath)
        if key not in existing_data:
            existing_data[key] = []
        existing_data[key].append(data)
        return save_json(existing_data, filepath)
    except Exception as e:
        print(f"Error appending to {filepath}: {e}")
        return False

def search_in_json(filepath: str, key: str, value: Any) -> Optional[Dict[str, Any]]:
    """Search for an item in JSON file"""
    try:
        data = load_json(filepath)
        items = data.get("items", [])
        for item in items:
            if item.get(key) == value:
                return item
        return None
    except Exception as e:
        print(f"Error searching in {filepath}: {e}")
        return None
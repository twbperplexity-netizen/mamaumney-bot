import json
import os
from typing import Dict, Any


DB_FILE = "users_data.json"


async def get_user(user_id: int) -> Dict[str, Any]:
    """
    Get user data from database by user ID.
    If user doesn't exist, return empty dict.
    """
    if not os.path.exists(DB_FILE):
        return {}
    
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        return data.get(str(user_id), {})
    except Exception:
        return {}


async def save_user(user_id: int, user_data: Dict[str, Any]) -> None:
    """
    Save user data to database.
    """
    all_data = {}
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                all_data = json.load(f)
        except Exception:
            all_data = {}
    
    all_data[str(user_id)] = user_data
    
    try:
        with open(DB_FILE, "w") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user data: {e}")


async def delete_user(user_id: int) -> None:
    """
    Delete user data from database.
    """
    if not os.path.exists(DB_FILE):
        return
    
    try:
        with open(DB_FILE, "r") as f:
            all_data = json.load(f)
        
        if str(user_id) in all_data:
            del all_data[str(user_id)]
        
        with open(DB_FILE, "w") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error deleting user data: {e}")

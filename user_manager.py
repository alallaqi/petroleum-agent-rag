import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserManager:
    """Simple user management system for tracking search limits"""
    
    def __init__(self):
        self.users_file = os.getenv("USERS_FILE", "users.json")
        self.enable_limits = os.getenv("ENABLE_USER_LIMITS", "true").lower() == "true"
        self.current_user_id = os.getenv("CURRENT_USER", "anonymous")
        self.users_data = self._load_users()
    
    def _load_users(self) -> Dict[str, Any]:
        """Load user data from JSON file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default structure if file doesn't exist
                return {
                    "users": {
                        "anonymous": {
                            "name": "Anonymous User",
                            "user_type": "anonymous",
                            "daily_search_limit": 1,
                            "current_usage": 0,
                            "last_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                            "active": True
                        }
                    },
                    "settings": {
                        "default_user": "anonymous",
                        "reset_time": "00:00",
                        "timezone": "UTC"
                    }
                }
        except Exception as e:
            print(f"Error loading users file: {e}")
            return {"users": {}, "settings": {}}
    
    def _save_users(self):
        """Save user data to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users file: {e}")
    
    def _reset_daily_usage_if_needed(self, user_id: str):
        """Reset daily usage if it's a new day"""
        if user_id not in self.users_data["users"]:
            return
        
        user = self.users_data["users"][user_id]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        if user.get("last_reset") != today:
            user["current_usage"] = 0
            user["last_reset"] = today
            self._save_users()
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        if self.current_user_id in self.users_data["users"]:
            user = self.users_data["users"][self.current_user_id].copy()
            user["user_id"] = self.current_user_id
            self._reset_daily_usage_if_needed(self.current_user_id)
            return user
        else:
            # Return anonymous user as fallback
            return self.get_user_info("anonymous")
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information for a specific user"""
        if user_id in self.users_data["users"]:
            user = self.users_data["users"][user_id].copy()
            user["user_id"] = user_id
            self._reset_daily_usage_if_needed(user_id)
            return user
        return {}
    
    def can_user_search(self, user_id: Optional[str] = None) -> tuple[bool, str]:
        """Check if user can perform a search"""
        if not self.enable_limits:
            return True, "Limits disabled"
        
        if user_id is None:
            user_id = self.current_user_id
        
        self._reset_daily_usage_if_needed(user_id)
        
        if user_id not in self.users_data["users"]:
            return False, "User not found"
        
        user = self.users_data["users"][user_id]
        
        if not user.get("active", True):
            return False, "User account is inactive"
        
        current_usage = user.get("current_usage", 0)
        daily_limit = user.get("daily_search_limit", 1)
        
        if current_usage >= daily_limit:
            return False, f"Daily search limit ({daily_limit}) reached. Resets at midnight UTC."
        
        return True, f"Searches remaining: {daily_limit - current_usage}"
    
    def increment_user_usage(self, user_id: Optional[str] = None) -> bool:
        """Increment user's search usage count"""
        if not self.enable_limits:
            return True
        
        if user_id is None:
            user_id = self.current_user_id
        
        if user_id not in self.users_data["users"]:
            return False
        
        self._reset_daily_usage_if_needed(user_id)
        
        user = self.users_data["users"][user_id]
        user["current_usage"] = user.get("current_usage", 0) + 1
        self._save_users()
        return True
    
    def switch_user(self, user_id: str) -> bool:
        """Switch current user"""
        if user_id in self.users_data["users"]:
            self.current_user_id = user_id
            return True
        return False
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users information"""
        users = {}
        for user_id, user_data in self.users_data["users"].items():
            self._reset_daily_usage_if_needed(user_id)
            users[user_id] = user_data.copy()
            users[user_id]["user_id"] = user_id
        return users
    
    def get_usage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        if user_id is None:
            user_id = self.current_user_id
        
        if user_id not in self.users_data["users"]:
            return {}
        
        self._reset_daily_usage_if_needed(user_id)
        user = self.users_data["users"][user_id]
        
        return {
            "user_id": user_id,
            "name": user.get("name", "Unknown"),
            "user_type": user.get("user_type", "unknown"),
            "current_usage": user.get("current_usage", 0),
            "daily_limit": user.get("daily_search_limit", 1),
            "remaining": user.get("daily_search_limit", 1) - user.get("current_usage", 0),
            "last_reset": user.get("last_reset", "Never")
        } 
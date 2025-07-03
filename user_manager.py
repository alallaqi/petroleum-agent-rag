import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserManager:
    """User management system for tracking keyword limits"""
    
    def __init__(self):
        self.users_file = os.getenv("USERS_FILE", "users.json")
        self.enable_limits = os.getenv("ENABLE_USER_LIMITS", "true").lower() == "true"
        self.current_user_id = os.getenv("CURRENT_USER", "anonymous")
        self.users_data = self._load_users()
        
        # Petroleum engineering keywords for extraction
        self.petroleum_keywords = {
            'drilling', 'fracking', 'hydraulic', 'fracturing', 'wellbore', 'casing', 'completion',
            'production', 'reservoir', 'petroleum', 'crude', 'natural', 'gas', 'oil', 'shale',
            'unconventional', 'conventional', 'permeability', 'porosity', 'saturation', 'pressure',
            'injection', 'extraction', 'recovery', 'enhanced', 'rig', 'offshore', 'onshore',
            'upstream', 'downstream', 'midstream', 'refinery', 'pipeline', 'transportation',
            'geology', 'geophysics', 'seismic', 'logging', 'mudlog', 'core', 'sample',
            'formation', 'rock', 'sand', 'carbonate', 'limestone', 'sandstone', 'mudstone',
            'tight', 'coal', 'bed', 'methane', 'horizontal', 'vertical', 'directional',
            'proppant', 'fluid', 'chemical', 'stimulation', 'acidizing', 'perforation',
            'flowback', 'produced', 'water', 'waste', 'environmental', 'safety', 'blowout',
            'well', 'borehole', 'tubing', 'pump', 'compressor', 'separator', 'manifold'
        }
    
    def _load_users(self) -> Dict[str, Any]:
        """Load user data from JSON file"""
        default_data = {
            "users": {
                "john_doe": {
                    "name": "John Doe",
                    "user_type": "registered",
                    "daily_keyword_limit": 10,
                    "current_keyword_usage": 0,
                    "last_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "active": True,
                    "query_history": []
                },
                "anonymous": {
                    "name": "Anonymous User",
                    "user_type": "anonymous", 
                    "daily_keyword_limit": 1,
                    "current_keyword_usage": 0,
                    "last_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "active": True,
                    "query_history": []
                }
            },
            "settings": {
                "default_user": "anonymous",
                "reset_time": "00:00",
                "timezone": "UTC"
            }
        }
        
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    # Migrate old data structure if needed
                    for user_id, user_data in data["users"].items():
                        if "daily_search_limit" in user_data:
                            # Migrate from search limits to keyword limits
                            user_data["daily_keyword_limit"] = user_data.pop("daily_search_limit")
                            user_data["current_keyword_usage"] = user_data.pop("current_usage", 0)
                            if "query_history" not in user_data:
                                user_data["query_history"] = []
                    return data
            else:
                # Create default file
                with open(self.users_file, 'w') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
                
        except Exception as e:
            print(f"Error loading users file: {e}")
            return default_data
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract petroleum-related keywords from query"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        
        # Find petroleum keywords
        found_keywords = []
        for word in words:
            if word in self.petroleum_keywords:
                found_keywords.append(word)
            # Also check for partial matches (e.g., "drilling" in "drilling rig")
            elif any(keyword in word for keyword in self.petroleum_keywords if len(keyword) > 4):
                # Add the petroleum keyword that matches
                for keyword in self.petroleum_keywords:
                    if keyword in word and len(keyword) > 4:
                        found_keywords.append(keyword)
                        break
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_keywords))
    
    def count_keywords_in_query(self, query: str) -> int:
        """Count petroleum keywords in a query"""
        keywords = self.extract_keywords(query)
        return len(keywords)
    
    def _save_users(self):
        """Save user data to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users file: {e}")
    
    def _reset_daily_usage_if_needed(self, user_data: Dict[str, Any]):
        """Reset usage if it's a new day"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if user_data.get("last_reset") != today:
            user_data["current_keyword_usage"] = 0
            user_data["last_reset"] = today
            user_data["query_history"] = []
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user data"""
        if self.current_user_id in self.users_data["users"]:
            user_data = self.users_data["users"][self.current_user_id].copy()
            user_data["user_id"] = self.current_user_id
            self._reset_daily_usage_if_needed(self.users_data["users"][self.current_user_id])
            return user_data
        return None
    
    def can_use_keywords(self, query: str) -> tuple[bool, int, int]:
        """
        Check if user can use keywords in this query
        Returns: (can_use, keywords_needed, keywords_remaining)
        """
        if not self.enable_limits:
            return True, 0, float('inf')
            
        user_data = self.users_data["users"].get(self.current_user_id)
        if not user_data:
            return False, 0, 0
            
        self._reset_daily_usage_if_needed(user_data)
        
        keywords_needed = self.count_keywords_in_query(query)
        keywords_used = user_data.get("current_keyword_usage", 0)
        keywords_limit = user_data.get("daily_keyword_limit", 1)
        keywords_remaining = max(0, keywords_limit - keywords_used)
        
        can_use = keywords_needed <= keywords_remaining
        return can_use, keywords_needed, keywords_remaining
    
    def use_keywords(self, query: str) -> bool:
        """
        Use keywords for current user and save query to history
        Returns True if successful, False if limit exceeded
        """
        if not self.enable_limits:
            return True
            
        can_use, keywords_needed, _ = self.can_use_keywords(query)
        
        if can_use:
            user_data = self.users_data["users"][self.current_user_id]
            user_data["current_keyword_usage"] = user_data.get("current_keyword_usage", 0) + keywords_needed
            
            # Add to query history
            query_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "query": query,
                "keywords_used": keywords_needed,
                "keywords_found": self.extract_keywords(query)
            }
            if "query_history" not in user_data:
                user_data["query_history"] = []
            user_data["query_history"].append(query_entry)
            
            self._save_users()
            return True
        
        return False
    
    def switch_user(self, new_user_id: str) -> bool:
        """Switch to a different user"""
        if new_user_id in self.users_data["users"]:
            self.current_user_id = new_user_id
            # Note: In a real app, you'd update the .env file or session
            return True
        return False
    
    def get_user_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed user statistics"""
        if user_id is None:
            user_id = self.current_user_id
            
        user_data = self.users_data["users"].get(user_id, {})
        self._reset_daily_usage_if_needed(user_data)
        
        return {
            "user_id": user_id,
            "name": user_data.get("name", "Unknown"),
            "user_type": user_data.get("user_type", "unknown"),
            "daily_keyword_limit": user_data.get("daily_keyword_limit", 0),
            "current_keyword_usage": user_data.get("current_keyword_usage", 0),
            "keywords_remaining": max(0, user_data.get("daily_keyword_limit", 0) - user_data.get("current_keyword_usage", 0)),
            "last_reset": user_data.get("last_reset", "Never"),
            "total_queries_today": len(user_data.get("query_history", [])),
            "active": user_data.get("active", False)
        }
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get list of all users with their basic info"""
        users = []
        for user_id, user_data in self.users_data["users"].items():
            users.append({
                "user_id": user_id,
                "name": user_data.get("name", "Unknown"),
                "user_type": user_data.get("user_type", "unknown"),
                "daily_keyword_limit": user_data.get("daily_keyword_limit", 0),
                "active": user_data.get("active", False)
            })
        return users 
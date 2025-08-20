"""
AI-powered learning and suggestion engine
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class LearningEngine:
    def __init__(self, db_path: str = None, debug_mode: bool = False):
        if db_path is None:
            db_path = Path.home() / ".smart_terminal" / "command_history.db"
        
        self.debug_mode = debug_mode
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_path)
        # Initialize database silently
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        # Check if database already exists and has correct schema
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='command_history'
                """)
                
                if cursor.fetchone():
                    # Database exists and has tables, just verify schema
                    try:
                        cursor.execute("PRAGMA table_info(command_history)")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        # Check if all required columns exist
                        required_columns = ['id', 'user_input', 'generated_command', 'success', 'execution_time', 'platform', 'timestamp']
                        if all(col in columns for col in required_columns):
                            conn.close()
                            return  # Database is fine, no need to recreate
                    except:
                        pass  # Schema check failed, will recreate
                
                conn.close()
                
                # Remove old database if schema is wrong
                try:
                    os.remove(self.db_path)
                    if self.debug_mode:
                        print("Database schema updated - old database removed")
                except Exception as e:
                    if self.debug_mode:
                        print(f"Warning: Could not remove old database: {e}")
                    
            except Exception as e:
                # Silently handle any database errors
                pass
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Command history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    generated_command TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    execution_time REAL,
                    platform TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Command patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Create a minimal working database silently
            self._create_minimal_database()
    
    def _create_minimal_database(self):
        """Create a minimal working database if the main one fails"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple command history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY,
                    user_input TEXT,
                    generated_command TEXT,
                    success INTEGER,
                    timestamp TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Silently fail - database operations will be skipped
            pass
    
    def record_command(self, user_input: str, command: str, success: bool, 
                      execution_time: float = None, platform: str = None):
        """Record a command execution for learning"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists and has correct schema
            cursor.execute("PRAGMA table_info(command_history)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'generated_command' not in columns:
                print("Database schema mismatch detected, recreating...")
                conn.close()
                self.init_database()
                return
            
            cursor.execute("""
                INSERT INTO command_history 
                (user_input, generated_command, success, execution_time, platform)
                VALUES (?, ?, ?, ?, ?)
            """, (user_input, command, success, execution_time, platform))
            
            conn.commit()
            conn.close()
            
            # Update pattern statistics
            self._update_pattern_stats(user_input, success)
            
        except Exception as e:
            print(f"Warning: Failed to record command: {e}")
            # Try to recreate database on next use
            if "no such column" in str(e):
                print("Attempting to fix database schema...")
                self.init_database()
    
    def _update_pattern_stats(self, pattern: str, success: bool):
        """Update statistics for command patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("PRAGMA table_info(command_patterns)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if not columns:
                conn.close()
                return
            
            # Check if pattern exists
            cursor.execute("SELECT id, success_rate, usage_count FROM command_patterns WHERE pattern = ?", (pattern,))
            result = cursor.fetchone()
            
            if result:
                pattern_id, current_success_rate, current_count = result
                new_count = current_count + 1
                new_success_rate = ((current_success_rate * current_count) + (1 if success else 0)) / new_count
                
                cursor.execute("""
                    UPDATE command_patterns 
                    SET success_rate = ?, usage_count = ?, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_success_rate, new_count, pattern_id))
            else:
                cursor.execute("""
                    INSERT INTO command_patterns (pattern, success_rate, usage_count)
                    VALUES (?, ?, 1)
                """, (pattern, 1.0 if success else 0.0))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Warning: Failed to update pattern stats: {e}")
    
    def get_suggestions(self, user_input: str, limit: int = 5) -> List[Dict]:
        """Get command suggestions based on user input and history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("PRAGMA table_info(command_patterns)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if not columns:
                conn.close()
                return []
            
            # Get similar successful commands
            cursor.execute("""
                SELECT pattern, success_rate, usage_count
                FROM command_patterns 
                WHERE pattern LIKE ? AND success_rate > 0.5
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT ?
            """, (f"%{user_input}%", limit))
            
            suggestions = []
            for row in cursor.fetchall():
                suggestions.append({
                    "command": row[0],
                    "confidence": row[1],
                    "usage_count": row[2]
                })
            
            conn.close()
            return suggestions
            
        except Exception as e:
            print(f"Warning: Failed to get suggestions: {e}")
            return []
    
    def get_user_stats(self) -> Dict:
        """Get user statistics and insights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("PRAGMA table_info(command_history)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if not columns:
                conn.close()
                return {
                    "total_commands": 0,
                    "success_rate": 0.0,
                    "top_patterns": [],
                    "platform_usage": []
                }
            
            # Total commands executed
            cursor.execute("SELECT COUNT(*) FROM command_history")
            total_commands = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) FROM command_history")
            success_rate = cursor.fetchone()[0] or 0.0
            
            # Most used patterns
            cursor.execute("""
                SELECT pattern, usage_count 
                FROM command_patterns 
                ORDER BY usage_count DESC 
                LIMIT 5
            """)
            top_patterns = [{"pattern": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Platform usage
            cursor.execute("""
                SELECT platform, COUNT(*) 
                FROM command_history 
                WHERE platform IS NOT NULL 
                GROUP BY platform
            """)
            platform_usage = [{"platform": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "total_commands": total_commands,
                "success_rate": round(success_rate * 100, 2),
                "top_patterns": top_patterns,
                "platform_usage": platform_usage
            }
            
        except Exception as e:
            print(f"Warning: Failed to get user stats: {e}")
            return {
                "total_commands": 0,
                "success_rate": 0.0,
                "top_patterns": [],
                "platform_usage": []
            }
    
    def save_preference(self, key: str, value: str):
        """Save a user preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (preference_key, preference_value)
                VALUES (?, ?)
            """, (key, value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Warning: Failed to save preference: {e}")
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT preference_value FROM user_preferences WHERE preference_key = ?
            """, (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else default
            
        except Exception as e:
            print(f"Warning: Failed to get preference: {e}")
            return default 
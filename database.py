import sqlite3
import datetime
from typing import Optional, List, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "academy.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_course INTEGER DEFAULT 1,
                current_module INTEGER DEFAULT 1,
                current_lesson INTEGER DEFAULT 1,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Course progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_id INTEGER,
                module_id INTEGER,
                lesson_id INTEGER,
                completed BOOLEAN DEFAULT FALSE,
                completion_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_name TEXT,
                achievement_type TEXT,
                date_awarded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Quiz attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_id INTEGER,
                module_id INTEGER,
                lesson_id INTEGER,
                score INTEGER,
                total_questions INTEGER,
                attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str):
        """Add new user or update existing user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO users (user_id, username, xp, level)
                VALUES (?, ?, COALESCE((SELECT xp FROM users WHERE user_id = ?), 0),
                        COALESCE((SELECT level FROM users WHERE user_id = ?), 1))
            """, (user_id, username, user_id, user_id))
            conn.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
        finally:
            conn.close()
    
    def add_xp(self, user_id: int, amount: int) -> int:
        """Add XP to user and return new total"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current XP
            cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return 0
            
            current_xp, current_level = result
            new_xp = current_xp + amount
            
            # Calculate new level (every 1000 XP = 1 level)
            new_level = (new_xp // 1000) + 1
            
            # Update user
            cursor.execute("""
                UPDATE users SET xp = ?, level = ? WHERE user_id = ?
            """, (new_xp, new_level, user_id))
            
            # Check for level up achievement
            if new_level > current_level:
                self.add_achievement(user_id, f"Level {new_level} Reached", "level_up")
            
            conn.commit()
            return new_xp
        except Exception as e:
            print(f"Error adding XP: {e}")
            return 0
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Optional[Tuple]:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT username, xp, level, current_course, current_module, current_lesson
                FROM users WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None
        finally:
            conn.close()
    
    def update_progress(self, user_id: int, course_id: int, module_id: int, lesson_id: int):
        """Update user's current progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Mark lesson as completed
            cursor.execute("""
                INSERT OR REPLACE INTO course_progress 
                (user_id, course_id, module_id, lesson_id, completed, completion_date)
                VALUES (?, ?, ?, ?, TRUE, CURRENT_TIMESTAMP)
            """, (user_id, course_id, module_id, lesson_id))
            
            # Update user's current position
            cursor.execute("""
                UPDATE users SET current_course = ?, current_module = ?, current_lesson = ?
                WHERE user_id = ?
            """, (course_id, module_id, lesson_id + 1, user_id))
            
            conn.commit()
        except Exception as e:
            print(f"Error updating progress: {e}")
        finally:
            conn.close()
    
    def add_achievement(self, user_id: int, achievement_name: str, achievement_type: str):
        """Add achievement to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if achievement already exists
            cursor.execute("""
                SELECT id FROM achievements 
                WHERE user_id = ? AND achievement_name = ?
            """, (user_id, achievement_name))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO achievements (user_id, achievement_name, achievement_type)
                    VALUES (?, ?, ?)
                """, (user_id, achievement_name, achievement_type))
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error adding achievement: {e}")
            return False
        finally:
            conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple]:
        """Get top users by XP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT username, xp, level FROM users 
                ORDER BY xp DESC LIMIT ?
            """, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_achievements(self, user_id: int) -> List[Tuple]:
        """Get all achievements for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT achievement_name, achievement_type, date_awarded
                FROM achievements WHERE user_id = ?
                ORDER BY date_awarded DESC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []
        finally:
            conn.close()
    
    def record_quiz_attempt(self, user_id: int, course_id: int, module_id: int, 
                           lesson_id: int, score: int, total_questions: int):
        """Record a quiz attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO quiz_attempts 
                (user_id, course_id, module_id, lesson_id, score, total_questions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, course_id, module_id, lesson_id, score, total_questions))
            conn.commit()
        except Exception as e:
            print(f"Error recording quiz attempt: {e}")
        finally:
            conn.close()

# Global database instance
db = DatabaseManager()

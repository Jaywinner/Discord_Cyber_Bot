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
        
        # CTF challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ctf_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_name TEXT UNIQUE,
                category TEXT,
                difficulty TEXT,
                points INTEGER,
                description TEXT,
                flag TEXT,
                hints TEXT,
                required_xp INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # CTF submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ctf_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                challenge_id INTEGER,
                submitted_flag TEXT,
                is_correct BOOLEAN,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (challenge_id) REFERENCES ctf_challenges (id)
            )
        """)
        
        # Multimedia content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS multimedia_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT, -- 'image', 'video', 'audio'
                content_url TEXT,
                content_description TEXT,
                course_id INTEGER,
                module_id INTEGER,
                lesson_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Check for level up achievement - use the same connection
            if new_level > current_level:
                self._add_achievement_with_connection(conn, cursor, user_id, f"Level {new_level} Reached", "level_up")
            
            conn.commit()
            return new_xp
        except Exception as e:
            print(f"Error adding XP: {e}")
            return 0
        finally:
            conn.close()
    
    def _add_achievement_with_connection(self, conn, cursor, user_id: int, achievement_name: str, achievement_type: str):
        """Add achievement using existing connection to prevent database locks"""
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
                return True
            return False
        except Exception as e:
            print(f"Error adding achievement: {e}")
            return False
    
    def add_xp_no_achievements(self, user_id: int, amount: int) -> int:
        """Add XP to user without triggering achievement checks (to prevent recursion)"""
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
            
            # Update user (no achievement checks)
            cursor.execute("""
                UPDATE users SET xp = ?, level = ? WHERE user_id = ?
            """, (new_xp, new_level, user_id))
            
            conn.commit()
            return new_xp
        except Exception as e:
            print(f"Error adding XP (no achievements): {e}")
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
    
    def update_user_progress(self, user_id: int, course_id: int, module_id: int, lesson_id: int):
        """Update user's current position without marking as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update user's current position
            cursor.execute("""
                UPDATE users SET current_course = ?, current_module = ?, current_lesson = ?
                WHERE user_id = ?
            """, (course_id, module_id, lesson_id, user_id))
            
            conn.commit()
        except Exception as e:
            print(f"Error updating user progress: {e}")
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
    
    # CTF Challenge Methods
    def add_ctf_challenge(self, name: str, category: str, difficulty: str, points: int, 
                         description: str, flag: str, hints: str = "", required_xp: int = 0):
        """Add a new CTF challenge"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ctf_challenges 
                (challenge_name, category, difficulty, points, description, flag, hints, required_xp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, category, difficulty, points, description, flag, hints, required_xp))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding CTF challenge: {e}")
            return False
        finally:
            conn.close()
    
    def get_ctf_challenges(self, user_xp: int = 0):
        """Get available CTF challenges based on user XP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, challenge_name, category, difficulty, points, description, required_xp
                FROM ctf_challenges 
                WHERE required_xp <= ?
                ORDER BY difficulty, points
            """, (user_xp,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting CTF challenges: {e}")
            return []
        finally:
            conn.close()
    
    def submit_ctf_flag(self, user_id: int, challenge_id: int, submitted_flag: str):
        """Submit a CTF flag and check if correct"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the correct flag
            cursor.execute("SELECT flag, points FROM ctf_challenges WHERE id = ?", (challenge_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Challenge not found"
            
            correct_flag, points = result
            is_correct = submitted_flag.strip() == correct_flag.strip()
            
            # Record the submission
            cursor.execute("""
                INSERT INTO ctf_submissions (user_id, challenge_id, submitted_flag, is_correct)
                VALUES (?, ?, ?, ?)
            """, (user_id, challenge_id, submitted_flag, is_correct))
            
            # If correct, award points
            if is_correct:
                self.add_xp(user_id, points)
            
            conn.commit()
            return is_correct, points if is_correct else 0
        except Exception as e:
            print(f"Error submitting CTF flag: {e}")
            return False, "Error processing submission"
        finally:
            conn.close()
    
    def get_user_ctf_progress(self, user_id: int):
        """Get user's CTF challenge progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT c.challenge_name, c.points, s.is_correct, s.submission_date
                FROM ctf_submissions s
                JOIN ctf_challenges c ON s.challenge_id = c.id
                WHERE s.user_id = ? AND s.is_correct = 1
                ORDER BY s.submission_date DESC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting CTF progress: {e}")
            return []
        finally:
            conn.close()
    
    # Multimedia Content Methods
    def add_multimedia_content(self, content_type: str, content_url: str, description: str,
                              course_id: int, module_id: int, lesson_id: int):
        """Add multimedia content to a lesson"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO multimedia_content 
                (content_type, content_url, content_description, course_id, module_id, lesson_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_type, content_url, description, course_id, module_id, lesson_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding multimedia content: {e}")
            return False
        finally:
            conn.close()
    
    def get_lesson_multimedia(self, course_id: int, module_id: int, lesson_id: int):
        """Get multimedia content for a specific lesson"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT content_type, content_url, content_description
                FROM multimedia_content 
                WHERE course_id = ? AND module_id = ? AND lesson_id = ?
            """, (course_id, module_id, lesson_id))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting multimedia content: {e}")
            return []
        finally:
            conn.close()

# Global database instance
db = DatabaseManager()

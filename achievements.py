"""
Achievement and Badge System for Cybersecurity Learning Bot
Tracks user progress and awards badges for milestones
"""

from database import db
import discord
from datetime import datetime

# Achievement definitions
ACHIEVEMENTS = {
    # XP-based achievements
    "first_steps": {
        "name": "🚀 First Steps",
        "description": "Complete your first lesson",
        "type": "lesson_completion",
        "requirement": 1,
        "xp_bonus": 50
    },
    "knowledge_seeker": {
        "name": "📚 Knowledge Seeker", 
        "description": "Complete 5 lessons",
        "type": "lesson_completion",
        "requirement": 5,
        "xp_bonus": 100
    },
    "cyber_student": {
        "name": "🎓 Cyber Student",
        "description": "Complete 10 lessons",
        "type": "lesson_completion", 
        "requirement": 10,
        "xp_bonus": 200
    },
    "security_scholar": {
        "name": "🏆 Security Scholar",
        "description": "Complete 25 lessons",
        "type": "lesson_completion",
        "requirement": 25,
        "xp_bonus": 500
    },
    
    # XP milestones
    "xp_novice": {
        "name": "⭐ XP Novice",
        "description": "Earn 500 XP",
        "type": "xp_milestone",
        "requirement": 500,
        "xp_bonus": 100
    },
    "xp_apprentice": {
        "name": "⭐⭐ XP Apprentice", 
        "description": "Earn 1,500 XP",
        "type": "xp_milestone",
        "requirement": 1500,
        "xp_bonus": 200
    },
    "xp_expert": {
        "name": "⭐⭐⭐ XP Expert",
        "description": "Earn 5,000 XP", 
        "type": "xp_milestone",
        "requirement": 5000,
        "xp_bonus": 500
    },
    "xp_master": {
        "name": "⭐⭐⭐⭐ XP Master",
        "description": "Earn 10,000 XP",
        "type": "xp_milestone", 
        "requirement": 10000,
        "xp_bonus": 1000
    },
    
    # Course completion achievements
    "fundamentals_graduate": {
        "name": "🛡️ Fundamentals Graduate",
        "description": "Complete Cybersecurity Fundamentals course",
        "type": "course_completion",
        "requirement": 1,
        "xp_bonus": 300
    },
    "password_master": {
        "name": "🔐 Password Master", 
        "description": "Complete Password Security Mastery course",
        "type": "course_completion",
        "requirement": 2,
        "xp_bonus": 300
    },
    "phishing_defender": {
        "name": "🎣 Phishing Defender",
        "description": "Complete Phishing Defense Academy course", 
        "type": "course_completion",
        "requirement": 3,
        "xp_bonus": 300
    },
    "network_guardian": {
        "name": "🌐 Network Guardian",
        "description": "Complete Network Security Basics course",
        "type": "course_completion", 
        "requirement": 4,
        "xp_bonus": 400
    },
    
    # Quiz achievements
    "quiz_ace": {
        "name": "🎯 Quiz Ace",
        "description": "Score 100% on 5 quizzes",
        "type": "perfect_quiz",
        "requirement": 5,
        "xp_bonus": 250
    },
    "quiz_champion": {
        "name": "🏅 Quiz Champion", 
        "description": "Score 100% on 15 quizzes",
        "type": "perfect_quiz",
        "requirement": 15,
        "xp_bonus": 500
    },
    
    # Streak achievements
    "daily_learner": {
        "name": "📅 Daily Learner",
        "description": "Complete lessons 3 days in a row",
        "type": "daily_streak",
        "requirement": 3,
        "xp_bonus": 150
    },
    "dedicated_student": {
        "name": "🔥 Dedicated Student",
        "description": "Complete lessons 7 days in a row", 
        "type": "daily_streak",
        "requirement": 7,
        "xp_bonus": 350
    },
    
    # Special achievements
    "early_adopter": {
        "name": "🌟 Early Adopter",
        "description": "One of the first 100 users",
        "type": "special",
        "requirement": 100,
        "xp_bonus": 200
    },
    "community_helper": {
        "name": "🤝 Community Helper",
        "description": "Help other learners in the community",
        "type": "special", 
        "requirement": 1,
        "xp_bonus": 300
    }
}

class AchievementManager:
    def __init__(self):
        self.db = db
    
    def check_and_award_achievements(self, user_id: int, achievement_type: str = None):
        """Check if user has earned any new achievements"""
        awarded_achievements = []
        
        # Get user stats
        user_stats = self.db.get_user_stats(user_id)
        if not user_stats:
            return awarded_achievements
        
        username, xp, level, current_course, current_module, current_lesson = user_stats
        
        # Get user's existing achievements
        existing_achievements = [ach[0] for ach in self.db.get_user_achievements(user_id)]
        
        # Check each achievement
        for achievement_id, achievement in ACHIEVEMENTS.items():
            if achievement["name"] in existing_achievements:
                continue  # User already has this achievement
            
            # Skip if checking specific type and this doesn't match
            if achievement_type and achievement["type"] != achievement_type:
                continue
            
            earned = False
            
            # Check XP milestones
            if achievement["type"] == "xp_milestone":
                if xp >= achievement["requirement"]:
                    earned = True
            
            # Check lesson completion count
            elif achievement["type"] == "lesson_completion":
                completed_lessons = self._count_completed_lessons(user_id)
                if completed_lessons >= achievement["requirement"]:
                    earned = True
            
            # Check course completion
            elif achievement["type"] == "course_completion":
                if self._is_course_completed(user_id, achievement["requirement"]):
                    earned = True
            
            # Check perfect quiz scores
            elif achievement["type"] == "perfect_quiz":
                perfect_quizzes = self._count_perfect_quizzes(user_id)
                if perfect_quizzes >= achievement["requirement"]:
                    earned = True
            
            # Award achievement if earned
            if earned:
                success = self.db.add_achievement(user_id, achievement["name"], achievement["type"])
                if success:
                    # Award bonus XP (but don't trigger recursive achievement checks)
                    self.db.add_xp_no_achievements(user_id, achievement["xp_bonus"])
                    awarded_achievements.append(achievement)
        
        return awarded_achievements
    
    def _count_completed_lessons(self, user_id: int) -> int:
        """Count total completed lessons for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM course_progress 
                WHERE user_id = ? AND completed = TRUE
            """, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error counting completed lessons: {e}")
            return 0
        finally:
            conn.close()
    
    def _is_course_completed(self, user_id: int, course_id: int) -> bool:
        """Check if user has completed all lessons in a course"""
        from courses import get_course
        
        course = get_course(course_id)
        if not course:
            return False
        
        # Count total lessons in course
        total_lessons = 0
        for module in course["modules"].values():
            total_lessons += len(module["lessons"])
        
        # Count completed lessons in course
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM course_progress 
                WHERE user_id = ? AND course_id = ? AND completed = TRUE
            """, (user_id, course_id))
            result = cursor.fetchone()
            completed_lessons = result[0] if result else 0
            
            return completed_lessons >= total_lessons
        except Exception as e:
            print(f"Error checking course completion: {e}")
            return False
        finally:
            conn.close()
    
    def _count_perfect_quizzes(self, user_id: int) -> int:
        """Count quizzes where user scored 100%"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM quiz_attempts 
                WHERE user_id = ? AND score = total_questions
            """, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error counting perfect quizzes: {e}")
            return 0
        finally:
            conn.close()
    
    def get_user_achievement_summary(self, user_id: int) -> dict:
        """Get comprehensive achievement summary for user"""
        achievements = self.db.get_user_achievements(user_id)
        user_stats = self.db.get_user_stats(user_id)
        
        if not user_stats:
            return {"error": "User not found"}
        
        username, xp, level, current_course, current_module, current_lesson = user_stats
        
        # Categorize achievements
        categorized = {
            "xp_milestone": [],
            "lesson_completion": [],
            "course_completion": [],
            "perfect_quiz": [],
            "daily_streak": [],
            "special": []
        }
        
        for achievement_name, achievement_type, date_awarded in achievements:
            categorized[achievement_type].append({
                "name": achievement_name,
                "date": date_awarded
            })
        
        # Calculate progress stats
        completed_lessons = self._count_completed_lessons(user_id)
        perfect_quizzes = self._count_perfect_quizzes(user_id)
        
        return {
            "username": username,
            "xp": xp,
            "level": level,
            "total_achievements": len(achievements),
            "completed_lessons": completed_lessons,
            "perfect_quizzes": perfect_quizzes,
            "achievements_by_category": categorized
        }
    
    def create_achievement_embed(self, achievement: dict, user_mention: str) -> discord.Embed:
        """Create Discord embed for achievement notification"""
        embed = discord.Embed(
            title="🎉 Achievement Unlocked!",
            description=f"{user_mention} earned: **{achievement['name']}**",
            color=0xFFD700  # Gold color
        )
        
        embed.add_field(
            name="Description",
            value=achievement["description"],
            inline=False
        )
        
        embed.add_field(
            name="Bonus XP",
            value=f"+{achievement['xp_bonus']} XP",
            inline=True
        )
        
        embed.set_footer(text="Keep learning to unlock more achievements!")
        embed.timestamp = datetime.utcnow()
        
        return embed
    
    def create_achievements_list_embed(self, user_id: int) -> discord.Embed:
        """Create embed showing all user achievements"""
        summary = self.get_user_achievement_summary(user_id)
        
        if "error" in summary:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found in database.",
                color=0xFF0000
            )
            return embed
        
        embed = discord.Embed(
            title=f"🏆 {summary['username']}'s Achievements",
            description=f"**Level {summary['level']}** • **{summary['xp']:,} XP** • **{summary['total_achievements']} Achievements**",
            color=0x00FF00
        )
        
        # Add achievement categories
        category_names = {
            "xp_milestone": "⭐ XP Milestones",
            "lesson_completion": "📚 Learning Progress", 
            "course_completion": "🎓 Course Completions",
            "perfect_quiz": "🎯 Quiz Mastery",
            "daily_streak": "🔥 Dedication",
            "special": "🌟 Special"
        }
        
        for category, achievements in summary["achievements_by_category"].items():
            if achievements:
                achievement_list = "\n".join([f"• {ach['name']}" for ach in achievements])
                embed.add_field(
                    name=category_names[category],
                    value=achievement_list,
                    inline=False
                )
        
        if summary["total_achievements"] == 0:
            embed.add_field(
                name="No achievements yet",
                value="Complete lessons and quizzes to start earning achievements!",
                inline=False
            )
        
        embed.add_field(
            name="📊 Progress Stats",
            value=f"• Lessons Completed: {summary['completed_lessons']}\n• Perfect Quiz Scores: {summary['perfect_quizzes']}",
            inline=False
        )
        
        return embed

# Global achievement manager instance
achievement_manager = AchievementManager()

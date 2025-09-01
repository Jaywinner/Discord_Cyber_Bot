"""
Interactive Quiz System for Cybersecurity Learning Bot
Handles quiz creation, user interactions, and scoring
"""

import discord
from discord.ui import Button, View
import asyncio
import random
from database import db
from achievements import achievement_manager
from courses import get_lesson

class QuizView(View):
    def __init__(self, quiz_data: dict, user_id: int, course_id: int, module_id: int, lesson_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.quiz_data = quiz_data
        self.user_id = user_id
        self.course_id = course_id
        self.module_id = module_id
        self.lesson_id = lesson_id
        self.answered = False
        self.correct_answer = quiz_data["correct"]
        
        # Create buttons for each option
        for i, option in enumerate(quiz_data["options"]):
            button = Button(
                label=f"{chr(65 + i)}. {option}",  # A, B, C, D
                style=discord.ButtonStyle.secondary,
                custom_id=f"quiz_option_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, option_index: int):
        """Create callback function for quiz option button"""
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "❌ This isn't your quiz! Use `!quiz` to start your own.",
                    ephemeral=True
                )
                return
            
            if self.answered:
                await interaction.response.send_message(
                    "❌ You've already answered this quiz!",
                    ephemeral=True
                )
                return
            
            self.answered = True
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            # Check if answer is correct
            is_correct = option_index == self.correct_answer
            
            # Create response embed
            if is_correct:
                embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"**Great job!** {self.quiz_data['explanation']}",
                    color=0x00FF00
                )
                xp_earned = 100
                db.add_xp(self.user_id, xp_earned)
                embed.add_field(
                    name="XP Earned",
                    value=f"+{xp_earned} XP",
                    inline=True
                )
                
                # Record perfect quiz attempt
                db.record_quiz_attempt(
                    self.user_id, self.course_id, self.module_id, 
                    self.lesson_id, 1, 1
                )
                
                # Check for achievements
                new_achievements = achievement_manager.check_and_award_achievements(
                    self.user_id, "perfect_quiz"
                )
                
                if new_achievements:
                    achievement_text = "\n".join([f"🏆 {ach['name']}" for ach in new_achievements])
                    embed.add_field(
                        name="New Achievements!",
                        value=achievement_text,
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="❌ Incorrect",
                    description=f"The correct answer was **{chr(65 + self.correct_answer)}. {self.quiz_data['options'][self.correct_answer]}**\n\n{self.quiz_data['explanation']}",
                    color=0xFF0000
                )
                embed.add_field(
                    name="Keep Learning!",
                    value="Review the lesson material and try again later.",
                    inline=False
                )
                
                # Record failed quiz attempt
                db.record_quiz_attempt(
                    self.user_id, self.course_id, self.module_id,
                    self.lesson_id, 0, 1
                )
            
            # Update the message with results
            await interaction.response.edit_message(embed=embed, view=self)
        
        return callback
    
    async def on_timeout(self):
        """Handle quiz timeout"""
        for item in self.children:
            item.disabled = True

class MultiQuizView(View):
    def __init__(self, questions: list, user_id: int, course_id: int, module_id: int, lesson_id: int):
        super().__init__(timeout=600)  # 10 minute timeout
        self.questions = questions
        self.user_id = user_id
        self.course_id = course_id
        self.module_id = module_id
        self.lesson_id = lesson_id
        self.current_question = 0
        self.score = 0
        self.answers = []
        
        # Create option buttons
        for i in range(4):  # Assuming max 4 options
            button = Button(
                label=f"{chr(65 + i)}.",  # A, B, C, D
                style=discord.ButtonStyle.secondary,
                custom_id=f"multi_quiz_option_{i}",
                row=0
            )
            button.callback = self.create_option_callback(i)
            self.add_item(button)
        
        # Add navigation buttons
        self.next_button = Button(
            label="Next Question ➡️",
            style=discord.ButtonStyle.primary,
            custom_id="next_question",
            disabled=True,
            row=1
        )
        self.next_button.callback = self.next_question
        self.add_item(self.next_button)
        
        self.finish_button = Button(
            label="Finish Quiz 🏁",
            style=discord.ButtonStyle.success,
            custom_id="finish_quiz",
            disabled=True,
            row=1
        )
        self.finish_button.callback = self.finish_quiz
        self.add_item(self.finish_button)
    
    def create_option_callback(self, option_index: int):
        """Create callback for option selection"""
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "❌ This isn't your quiz!",
                    ephemeral=True
                )
                return
            
            # Record answer
            current_q = self.questions[self.current_question]
            is_correct = option_index == current_q["correct"]
            
            self.answers.append({
                "question_index": self.current_question,
                "selected": option_index,
                "correct": current_q["correct"],
                "is_correct": is_correct
            })
            
            if is_correct:
                self.score += 1
            
            # Disable option buttons and enable next/finish
            for item in self.children[:4]:  # First 4 are option buttons
                item.disabled = True
                if item.custom_id == f"multi_quiz_option_{option_index}":
                    item.style = discord.ButtonStyle.success if is_correct else discord.ButtonStyle.danger
            
            # Enable appropriate navigation button
            if self.current_question < len(self.questions) - 1:
                self.next_button.disabled = False
            else:
                self.finish_button.disabled = False
            
            # Show immediate feedback
            feedback = "✅ Correct!" if is_correct else f"❌ Incorrect. The answer was {chr(65 + current_q['correct'])}."
            
            embed = self.create_question_embed()
            embed.add_field(
                name="Answer",
                value=feedback,
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
        
        return callback
    
    async def next_question(self, interaction: discord.Interaction):
        """Move to next question"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your quiz!",
                ephemeral=True
            )
            return
        
        self.current_question += 1
        
        # Reset buttons for next question
        for item in self.children[:4]:  # Option buttons
            item.disabled = False
            item.style = discord.ButtonStyle.secondary
        
        self.next_button.disabled = True
        self.finish_button.disabled = True
        
        # Update question display
        embed = self.create_question_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def finish_quiz(self, interaction: discord.Interaction):
        """Finish quiz and show results"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your quiz!",
                ephemeral=True
            )
            return
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Calculate results
        total_questions = len(self.questions)
        percentage = (self.score / total_questions) * 100
        
        # Create results embed
        embed = discord.Embed(
            title="🎯 Quiz Complete!",
            description=f"**Score: {self.score}/{total_questions} ({percentage:.1f}%)**",
            color=0x00FF00 if percentage >= 70 else 0xFFAA00 if percentage >= 50 else 0xFF0000
        )
        
        # Add performance message
        if percentage >= 90:
            embed.add_field(name="Performance", value="🌟 Excellent! You're a cybersecurity star!", inline=False)
        elif percentage >= 70:
            embed.add_field(name="Performance", value="👍 Good job! You're getting the hang of this!", inline=False)
        elif percentage >= 50:
            embed.add_field(name="Performance", value="📚 Not bad, but review the material and try again!", inline=False)
        else:
            embed.add_field(name="Performance", value="📖 Keep studying! Review the lessons and come back stronger!", inline=False)
        
        # Award XP based on performance
        base_xp = 50
        bonus_xp = self.score * 25
        total_xp = base_xp + bonus_xp
        
        db.add_xp(self.user_id, total_xp)
        embed.add_field(name="XP Earned", value=f"+{total_xp} XP", inline=True)
        
        # Record quiz attempt
        db.record_quiz_attempt(
            self.user_id, self.course_id, self.module_id,
            self.lesson_id, self.score, total_questions
        )
        
        # Check for achievements
        achievement_types = ["perfect_quiz"] if self.score == total_questions else []
        new_achievements = []
        for ach_type in achievement_types:
            new_achievements.extend(
                achievement_manager.check_and_award_achievements(self.user_id, ach_type)
            )
        
        if new_achievements:
            achievement_text = "\n".join([f"🏆 {ach['name']}" for ach in new_achievements])
            embed.add_field(
                name="New Achievements!",
                value=achievement_text,
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_question_embed(self) -> discord.Embed:
        """Create embed for current question"""
        current_q = self.questions[self.current_question]
        
        embed = discord.Embed(
            title=f"❓ Question {self.current_question + 1}/{len(self.questions)}",
            description=current_q["question"],
            color=0x0099FF
        )
        
        # Add options
        options_text = ""
        for i, option in enumerate(current_q["options"]):
            options_text += f"**{chr(65 + i)}.** {option}\n"
        
        embed.add_field(
            name="Options",
            value=options_text,
            inline=False
        )
        
        embed.add_field(
            name="Progress",
            value=f"Score: {self.score}/{self.current_question} so far",
            inline=True
        )
        
        return embed

class QuizManager:
    def __init__(self):
        self.db = db
    
    async def start_lesson_quiz(self, ctx, course_id: int, module_id: int, lesson_id: int):
        """Start a quiz for a specific lesson"""
        lesson = get_lesson(course_id, module_id, lesson_id)
        
        if not lesson or "quiz" not in lesson:
            embed = discord.Embed(
                title="❌ No Quiz Available",
                description="This lesson doesn't have a quiz yet.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        quiz_data = lesson["quiz"]
        
        # Create quiz embed
        embed = discord.Embed(
            title=f"❓ {lesson['title']} - Quiz",
            description=quiz_data["question"],
            color=0x0099FF
        )
        
        # Add options
        options_text = ""
        for i, option in enumerate(quiz_data["options"]):
            options_text += f"**{chr(65 + i)}.** {option}\n"
        
        embed.add_field(
            name="Choose your answer:",
            value=options_text,
            inline=False
        )
        
        embed.set_footer(text="You have 5 minutes to answer!")
        
        # Create view with buttons
        view = QuizView(quiz_data, ctx.author.id, course_id, module_id, lesson_id)
        
        await ctx.send(embed=embed, view=view)
    
    async def start_module_quiz(self, ctx, course_id: int, module_id: int):
        """Start a comprehensive quiz for a module"""
        from courses import get_module
        
        module = get_module(course_id, module_id)
        if not module:
            embed = discord.Embed(
                title="❌ Module Not Found",
                description="Could not find the specified module.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Collect all quiz questions from module lessons
        questions = []
        for lesson_id, lesson in module["lessons"].items():
            if "quiz" in lesson:
                questions.append(lesson["quiz"])
        
        if not questions:
            embed = discord.Embed(
                title="❌ No Quizzes Available",
                description="This module doesn't have any quizzes yet.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Shuffle questions for variety
        random.shuffle(questions)
        
        # Limit to 5 questions max for better UX
        questions = questions[:5]
        
        # Create initial embed
        embed = discord.Embed(
            title=f"🎯 {module['title']} - Module Quiz",
            description=f"Test your knowledge with {len(questions)} questions from this module!",
            color=0x0099FF
        )
        
        embed.add_field(
            name="Instructions",
            value="• Answer each question by clicking the correct option\n• You'll see immediate feedback\n• Click 'Next' to continue or 'Finish' when done",
            inline=False
        )
        
        # Create multi-quiz view
        view = MultiQuizView(questions, ctx.author.id, course_id, module_id, 0)
        
        await ctx.send(embed=embed)
        
        # Start first question after a brief delay
        await asyncio.sleep(2)
        question_embed = view.create_question_embed()
        await ctx.send(embed=question_embed, view=view)
    
    async def get_quiz_stats(self, ctx, user_id: int = None):
        """Get quiz statistics for a user"""
        target_user_id = user_id or ctx.author.id
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get quiz statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_percentage,
                    SUM(CASE WHEN score = total_questions THEN 1 ELSE 0 END) as perfect_scores,
                    MAX(CAST(score AS FLOAT) / total_questions * 100) as best_percentage
                FROM quiz_attempts 
                WHERE user_id = ?
            """, (target_user_id,))
            
            stats = cursor.fetchone()
            
            if not stats or stats[0] == 0:
                embed = discord.Embed(
                    title="📊 Quiz Statistics",
                    description="No quiz attempts yet! Take some quizzes to see your stats.",
                    color=0x0099FF
                )
                await ctx.send(embed=embed)
                return
            
            total_attempts, avg_percentage, perfect_scores, best_percentage = stats
            
            # Get user info
            user_stats = self.db.get_user_stats(target_user_id)
            username = user_stats[0] if user_stats else "Unknown User"
            
            embed = discord.Embed(
                title=f"📊 {username}'s Quiz Statistics",
                color=0x00FF00
            )
            
            embed.add_field(
                name="📈 Overall Performance",
                value=f"• **Total Attempts:** {total_attempts}\n• **Average Score:** {avg_percentage:.1f}%\n• **Best Score:** {best_percentage:.1f}%",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Perfect Scores",
                value=f"**{perfect_scores}** out of {total_attempts} attempts ({(perfect_scores/total_attempts*100):.1f}%)",
                inline=False
            )
            
            # Performance rating
            if avg_percentage >= 90:
                rating = "🌟 Cybersecurity Expert"
            elif avg_percentage >= 80:
                rating = "🏆 Security Specialist"
            elif avg_percentage >= 70:
                rating = "👍 Good Student"
            elif avg_percentage >= 60:
                rating = "📚 Learning in Progress"
            else:
                rating = "📖 Keep Studying!"
            
            embed.add_field(
                name="🎖️ Performance Rating",
                value=rating,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Error getting quiz stats: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not retrieve quiz statistics.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        finally:
            conn.close()

# Global quiz manager instance
quiz_manager = QuizManager()

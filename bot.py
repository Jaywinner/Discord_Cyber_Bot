"""
Enhanced Cybersecurity Learning Discord Bot
Interactive, gamified cybersecurity education platform
"""

import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from database import db
from courses import get_course, get_lesson, get_next_lesson, get_course_list, get_module
from achievements import achievement_manager
from quiz import quiz_manager
from admin import AdminCommands
from ctf import ctf_manager, CTFChallengeView
from multimedia import multimedia_manager

# Bot configuration
PREFIX = "!"
GUILD_ID = 1394809146036977795  # Replace with your server ID

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

class CourseSelectionView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        
        # Add course selection buttons
        courses = get_course_list()
        for course in courses[:5]:  # Limit to 5 courses to avoid button limit
            button = Button(
                label=f"{course['title'][:20]}...",
                style=discord.ButtonStyle.primary,
                custom_id=f"course_{course['id']}"
            )
            button.callback = self.select_course
            self.add_item(button)
    
    async def select_course(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            try:
                await interaction.response.send_message(
                    "❌ This isn't your course selection! Use `/start` to begin your own journey.",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                # Interaction expired, ignore
                pass
            return
        
        # Extract course ID from custom_id
        course_id = int(interaction.data['custom_id'].split('_')[1])
        course = get_course(course_id)
        
        # Update user's progress to start this course
        db.update_user_progress(self.user_id, course_id, 1, 1)
        
        try:
            await interaction.response.send_message(
                f"🎉 Great choice! You've selected **{course['title']}**\n"
                f"📖 Starting your first lesson...",
                ephemeral=True
            )
            
            # Show the first lesson
            await show_lesson(interaction.followup, course_id, 1, 1, self.user_id)
        except discord.errors.NotFound:
            # Interaction expired, send a new message instead
            channel = interaction.channel if hasattr(interaction, 'channel') else None
            if channel:
                await show_lesson(channel, course_id, 1, 1, self.user_id)

class LessonView(View):
    def __init__(self, user_id: int, course_id: int, module_id: int, lesson_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.course_id = course_id
        self.module_id = module_id
        self.lesson_id = lesson_id
    
    @discord.ui.button(label="✅ Complete Lesson", style=discord.ButtonStyle.green)
    async def complete_lesson(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            try:
                await interaction.response.send_message(
                    "❌ This isn't your lesson! Use `/start` to begin your own journey.",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                # Interaction expired, ignore
                pass
            return
        
        # Get lesson data
        lesson = get_lesson(self.course_id, self.module_id, self.lesson_id)
        if not lesson:
            try:
                await interaction.response.send_message("❌ Lesson not found.", ephemeral=True)
            except discord.errors.NotFound:
                # Interaction expired, ignore
                pass
            return
        
        # Add user to database if not exists
        db.add_user(interaction.user.id, interaction.user.display_name)
        
        # Award XP
        xp_reward = lesson.get("xp_reward", 100)
        new_xp = db.add_xp(interaction.user.id, xp_reward)
        
        # Update progress to next lesson
        next_lesson_info = get_next_lesson(self.course_id, self.module_id, self.lesson_id)
        if next_lesson_info:
            next_course_id, next_module_id, next_lesson_id = next_lesson_info
            db.update_user_progress(interaction.user.id, next_course_id, next_module_id, next_lesson_id)
        
        # Update completion progress
        db.update_progress(interaction.user.id, self.course_id, self.module_id, self.lesson_id)
        
        # Check for achievements
        new_achievements = achievement_manager.check_and_award_achievements(interaction.user.id)
        
        # Create completion embed
        embed = discord.Embed(
            title="🎉 Lesson Complete!",
            description=f"**{lesson['title']}** completed successfully!",
            color=0x00FF00
        )
        
        embed.add_field(name="XP Earned", value=f"+{xp_reward} XP", inline=True)
        embed.add_field(name="Total XP", value=f"{new_xp:,} XP", inline=True)
        
        if new_achievements:
            achievement_text = "\n".join([f"🏆 {ach['name']}" for ach in new_achievements])
            embed.add_field(
                name="🎉 New Achievements!",
                value=achievement_text,
                inline=False
            )
        
        # Disable the complete button
        button.disabled = True
        button.label = "✅ Completed"
        
        # Create new view with progression options
        new_view = View(timeout=300)
        
        # Check for next lesson
        if next_lesson_info:
            next_course_id, next_module_id, next_lesson_id = next_lesson_info
            next_lesson = get_lesson(next_course_id, next_module_id, next_lesson_id)
            next_course = get_course(next_course_id)
            
            # Check if we're moving to a new course
            if next_course_id != self.course_id:
                embed.add_field(
                    name="🎓 Course Complete!",
                    value=f"You've finished **{get_course(self.course_id)['title']}**!\n"
                          f"Ready to start **{next_course['title']}**?",
                    inline=False
                )
                next_button_label = f"🚀 Start Next Course"
            else:
                embed.add_field(
                    name="📚 What's Next?",
                    value=f"Ready for your next lesson: **{next_lesson['title']}**?",
                    inline=False
                )
                next_button_label = f"📖 Next Lesson"
            
            # Add next lesson button
            async def next_lesson_callback(inter):
                if inter.user.id != self.user_id:
                    try:
                        await inter.response.send_message("❌ This isn't your journey!", ephemeral=True)
                    except discord.errors.NotFound:
                        # Interaction expired, ignore
                        pass
                    return
                try:
                    await inter.response.send_message("📖 Loading next lesson...", ephemeral=True)
                    await show_lesson(inter.followup, next_course_id, next_module_id, next_lesson_id, self.user_id)
                except discord.errors.NotFound:
                    # Interaction expired, send a new message instead
                    channel = inter.channel if hasattr(inter, 'channel') else None
                    if channel:
                        await show_lesson(channel, next_course_id, next_module_id, next_lesson_id, self.user_id)
            
            next_button = Button(label=next_button_label, style=discord.ButtonStyle.primary)
            next_button.callback = next_lesson_callback
            new_view.add_item(next_button)
        else:
            embed.add_field(
                name="🎓 Congratulations!",
                value="You've completed all available content! Amazing work on your cybersecurity journey!",
                inline=False
            )
        
        # Add browse courses button
        async def browse_courses_callback(inter):
            if inter.user.id != self.user_id:
                try:
                    await inter.response.send_message("❌ This isn't your journey!", ephemeral=True)
                except discord.errors.NotFound:
                    # Interaction expired, ignore
                    pass
                return
            try:
                await inter.response.send_message("📚 Loading course catalog...", ephemeral=True)
                await list_courses_with_selection(inter.followup, self.user_id)
            except discord.errors.NotFound:
                # Interaction expired, send a new message instead
                channel = inter.channel if hasattr(inter, 'channel') else None
                if channel:
                    await list_courses_with_selection(channel, self.user_id)
        
        browse_button = Button(label="📚 Browse Courses", style=discord.ButtonStyle.secondary)
        browse_button.callback = browse_courses_callback
        new_view.add_item(browse_button)
        
        try:
            await interaction.response.edit_message(embed=embed, view=new_view)
        except discord.errors.NotFound:
            # Interaction expired, send a new message instead
            channel = interaction.channel if hasattr(interaction, 'channel') else None
            if channel:
                await channel.send(embed=embed, view=new_view)
        
        # Send DM with achievement notifications
        if new_achievements:
            try:
                dm_embed = discord.Embed(
                    title="🏆 Achievement Unlocked!",
                    color=0xFFD700
                )
                for achievement in new_achievements:
                    dm_embed.add_field(
                        name=achievement["name"],
                        value=f"{achievement['description']}\n+{achievement['xp_bonus']} Bonus XP",
                        inline=False
                    )
                await interaction.user.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
    
    @discord.ui.button(label="❓ Take Quiz", style=discord.ButtonStyle.primary)
    async def take_quiz(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            try:
                await interaction.response.send_message(
                    "❌ This isn't your lesson! Use `/start` to begin your own journey.",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                # Interaction expired, ignore
                pass
            return
        
        # Check if lesson has a quiz
        lesson = get_lesson(self.course_id, self.module_id, self.lesson_id)
        if not lesson or "quiz" not in lesson:
            try:
                await interaction.response.send_message(
                    "❌ This lesson doesn't have a quiz available.",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                # Interaction expired, ignore
                pass
            return
        
        try:
            await interaction.response.send_message(
                "🎯 Starting quiz... Check the new message below!",
                ephemeral=True
            )
            
            # Start the quiz
            await quiz_manager.start_lesson_quiz(
                interaction.followup, self.course_id, self.module_id, self.lesson_id, self.user_id
            )
        except discord.errors.NotFound:
            # Interaction expired, send quiz directly to channel
            channel = interaction.channel if hasattr(interaction, 'channel') else None
            if channel:
                await quiz_manager.start_lesson_quiz(
                    channel, self.course_id, self.module_id, self.lesson_id, self.user_id
                )

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready to teach cybersecurity!")
    print(f"📚 Loaded courses: {len(get_course_list())}")
    
    # Sync slash commands (optional)
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="start", description="🚀 Start your cybersecurity learning journey!")
async def start_journey(interaction: discord.Interaction):
    """🚀 Start your cybersecurity learning journey!"""
    
    # Add user to database
    db.add_user(interaction.user.id, interaction.user.display_name)
    
    # Get user stats
    user_stats = db.get_user_stats(interaction.user.id)
    
    # Check if this is a new user (no progress yet)
    if not user_stats or user_stats[1] == 0:  # No XP means new user
        # Show course selection for new users
        embed = discord.Embed(
            title="🚀 Welcome to Cyber Academy!",
            description=f"Welcome **{interaction.user.display_name}**! Choose your cybersecurity learning path:",
            color=0x0099FF
        )
        
        courses = get_course_list()
        course_descriptions = []
        for course in courses:
            course_descriptions.append(f"**{course['title']}** ({course['level']})\n{course['description']}")
        
        embed.add_field(
            name="📚 Available Courses",
            value="\n\n".join(course_descriptions),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Getting Started",
            value="Select a course below to begin your cybersecurity journey!\nEach course contains multiple modules with hands-on lessons.",
            inline=False
        )
        
        embed.set_footer(text="Choose wisely! You can always switch courses later.")
        
        # Create course selection view
        view = CourseSelectionView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    else:
        # Existing user - show progress and continue
        username, xp, level, current_course, current_module, current_lesson = user_stats
        
        # Get current lesson
        lesson = get_lesson(current_course, current_module, current_lesson)
        course = get_course(current_course)
        
        if not lesson or not course:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not find your current lesson. Please contact an administrator.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create welcome back embed
        embed = discord.Embed(
            title="🚀 Welcome Back to Cyber Academy!",
            description=f"Ready to continue your cybersecurity journey, **{interaction.user.display_name}**?",
            color=0x0099FF
        )
        
        embed.add_field(
            name="📊 Your Progress",
            value=f"• **Level:** {level}\n• **XP:** {xp:,}\n• **Current Course:** {course['title']}",
            inline=False
        )
        
        embed.add_field(
            name="📚 Next Lesson",
            value=f"**{lesson['title']}**\nCourse {current_course} • Module {current_module} • Lesson {current_lesson}",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Quick Commands",
            value="• `/lesson` - View current lesson\n• `/courses` - Browse all courses\n• `/progress` - Check your progress\n• `/leaderboard` - See top learners",
            inline=False
        )
        
        embed.set_footer(text="Click the button below to continue your learning!")
        
        # Create continue button
        view = View(timeout=300)
        
        async def continue_lesson(button_interaction):
            if button_interaction.user.id != interaction.user.id:
                try:
                    await button_interaction.response.send_message(
                        "❌ This isn't your journey! Use `/start` to begin your own.",
                        ephemeral=True
                    )
                except discord.errors.NotFound:
                    # Interaction expired, ignore
                    pass
                return
            
            try:
                await button_interaction.response.send_message(
                    f"📖 Loading lesson: **{lesson['title']}**...",
                    ephemeral=True
                )
                
                # Show the lesson
                await show_lesson(button_interaction.followup, current_course, current_module, current_lesson, interaction.user.id)
            except discord.errors.NotFound:
                # Interaction expired, send lesson directly to channel
                channel = button_interaction.channel if hasattr(button_interaction, 'channel') else None
                if channel:
                    await show_lesson(channel, current_course, current_module, current_lesson, interaction.user.id)
        
        continue_button = Button(label="📖 Continue Learning", style=discord.ButtonStyle.green)
        continue_button.callback = continue_lesson
        view.add_item(continue_button)
        
        # Add course selection button for existing users too
        async def select_new_course(button_interaction):
            if button_interaction.user.id != interaction.user.id:
                try:
                    await button_interaction.response.send_message("❌ This isn't your journey!", ephemeral=True)
                except discord.errors.NotFound:
                    # Interaction expired, ignore
                    pass
                return
            try:
                await button_interaction.response.send_message("📚 Loading course selection...", ephemeral=True)
                await list_courses_with_selection(button_interaction.followup, interaction.user.id)
            except discord.errors.NotFound:
                # Interaction expired, send course selection directly to channel
                channel = button_interaction.channel if hasattr(button_interaction, 'channel') else None
                if channel:
                    await list_courses_with_selection(channel, interaction.user.id)
        
        course_button = Button(label="📚 Choose Different Course", style=discord.ButtonStyle.secondary)
        course_button.callback = select_new_course
        view.add_item(course_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def show_lesson(ctx_or_followup, course_id: int, module_id: int, lesson_id: int, user_id: int = None):
    """Internal function to show a lesson - works with both ctx and followup"""
    
    # Determine user_id if not provided
    if user_id is None:
        if hasattr(ctx_or_followup, 'author'):
            user_id = ctx_or_followup.author.id
        else:
            # This shouldn't happen, but fallback
            return
    
    # Add user to database
    db.add_user(user_id, "User")  # We'll update the name later if needed
    
    # Get lesson and course data
    lesson = get_lesson(course_id, module_id, lesson_id)
    course = get_course(course_id)
    
    if not lesson:
        embed = discord.Embed(
            title="❌ Lesson Not Found",
            description="Could not find the specified lesson.",
            color=0xFF0000
        )
        if hasattr(ctx_or_followup, 'send'):
            await ctx_or_followup.send(embed=embed)
        else:
            await ctx_or_followup.send(embed=embed)
        return
    
    # Create lesson embed
    embed = discord.Embed(
        title=f"📖 {lesson['title']}",
        description=lesson['content'],
        color=0x0099FF
    )
    
    embed.add_field(
        name="📚 Course Info",
        value=f"**{course['title']}**\nCourse {course_id} • Module {module_id} • Lesson {lesson_id}",
        inline=True
    )
    
    embed.add_field(
        name="⭐ XP Reward",
        value=f"{lesson.get('xp_reward', 100)} XP",
        inline=True
    )
    
    # Add practical exercise if available
    if "practical_exercise" in lesson:
        exercise = lesson["practical_exercise"]
        embed.add_field(
            name="🛠️ Practical Exercise",
            value=f"**{exercise['title']}**\n{exercise['description']}",
            inline=False
        )
    
    # Add quiz info if available
    if "quiz" in lesson:
        embed.add_field(
            name="🎯 Quiz Available",
            value="Test your knowledge with the lesson quiz!",
            inline=False
        )
    
    embed.set_footer(text="Complete the lesson to earn XP and unlock achievements!")
    
    # Create lesson view with interactive buttons
    view = LessonView(user_id, course_id, module_id, lesson_id)
    
    if hasattr(ctx_or_followup, 'send'):
        await ctx_or_followup.send(embed=embed, view=view)
    else:
        await ctx_or_followup.send(embed=embed, view=view)

async def list_courses_with_selection(ctx_or_followup, user_id: int):
    """Show course list with selection buttons"""
    
    courses = get_course_list()
    
    embed = discord.Embed(
        title="📚 Course Catalog",
        description="Choose a course to start or switch to:",
        color=0x0099FF
    )
    
    for course in courses:
        embed.add_field(
            name=f"{course['title']} ({course['level']})",
            value=f"{course['description']}\n\n",
            inline=False
        )
    
    embed.set_footer(text="Select a course below to begin!")
    
    # Create course selection view
    view = CourseSelectionView(user_id)
    
    if hasattr(ctx_or_followup, 'send'):
        await ctx_or_followup.send(embed=embed, view=view)
    else:
        await ctx_or_followup.send(embed=embed, view=view)

@bot.tree.command(name="lesson", description="📖 View a specific lesson or your current lesson")
async def lesson_command(interaction: discord.Interaction, course_id: int = None, module_id: int = None, lesson_id: int = None):
    """📖 View a specific lesson or your current lesson"""
    
    # Add user to database
    db.add_user(interaction.user.id, interaction.user.display_name)
    
    # If no parameters provided, show current lesson
    if not all([course_id, module_id, lesson_id]):
        user_stats = db.get_user_stats(interaction.user.id)
        if user_stats:
            _, _, _, course_id, module_id, lesson_id = user_stats
        else:
            course_id, module_id, lesson_id = 1, 1, 1
    
    # Send initial response
    await interaction.response.send_message("📖 Loading lesson...", ephemeral=True)
    
    # Use the internal show_lesson function
    await show_lesson(interaction.followup, course_id, module_id, lesson_id, interaction.user.id)

@bot.tree.command(name="courses", description="📚 Browse all available courses")
async def list_courses(interaction: discord.Interaction):
    """📚 Browse all available courses"""
    
    courses = get_course_list()
    
    embed = discord.Embed(
        title="📚 Available Courses",
        description="Choose your cybersecurity learning path:",
        color=0x0099FF
    )
    
    for course in courses:
        embed.add_field(
            name=f"{course['title']} ({course['level']})",
            value=f"{course['description']}\nUse `/lesson {course['id']} 1 1` to start",
            inline=False
        )
    
    embed.set_footer(text="More courses coming soon!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="progress", description="📊 Check your learning progress")
async def show_progress(interaction: discord.Interaction, user: discord.Member = None):
    """📊 Check your learning progress"""
    
    target_user = user or interaction.user
    
    # Add user to database
    db.add_user(target_user.id, target_user.display_name)
    
    user_stats = db.get_user_stats(target_user.id)
    if not user_stats:
        embed = discord.Embed(
            title="❌ No Progress Found",
            description="Start learning with `/start` to track your progress!",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    username, xp, level, current_course, current_module, current_lesson = user_stats
    
    # Get achievement summary
    achievement_summary = achievement_manager.get_user_achievement_summary(target_user.id)
    
    embed = discord.Embed(
        title=f"📊 {username}'s Progress",
        color=0x00FF00
    )
    
    embed.add_field(
        name="📈 Stats",
        value=f"• **Level:** {level}\n• **XP:** {xp:,}\n• **Achievements:** {achievement_summary['total_achievements']}",
        inline=True
    )
    
    embed.add_field(
        name="📚 Learning Progress",
        value=f"• **Current Course:** {current_course}\n• **Current Module:** {current_module}\n• **Current Lesson:** {current_lesson}",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Activity",
        value=f"• **Lessons Completed:** {achievement_summary['completed_lessons']}\n• **Perfect Quiz Scores:** {achievement_summary['perfect_quizzes']}",
        inline=True
    )
    
    # XP to next level
    xp_to_next = ((level * 1000) - xp)
    if xp_to_next > 0:
        embed.add_field(
            name="⬆️ Next Level",
            value=f"{xp_to_next:,} XP needed for Level {level + 1}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="leaderboard", description="🏆 View the top cybersecurity learners")
async def show_leaderboard(interaction: discord.Interaction):
    """🏆 View the top cybersecurity learners"""
    
    leaderboard = db.get_leaderboard(10)
    
    if not leaderboard:
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="No learners yet! Be the first to start your cybersecurity journey!",
            color=0xFFD700
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🏆 Cybersecurity Leaderboard",
        description="Top learners in our academy:",
        color=0xFFD700
    )
    
    medals = ["🥇", "🥈", "🥉"]
    
    leaderboard_text = ""
    for i, (username, xp, level) in enumerate(leaderboard):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        leaderboard_text += f"{medal} **{username}** - Level {level} ({xp:,} XP)\n"
    
    embed.add_field(
        name="Rankings",
        value=leaderboard_text,
        inline=False
    )
    
    embed.set_footer(text="Keep learning to climb the ranks!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="quiz", description="🎯 Take a quiz for a lesson or module")
async def start_quiz(interaction: discord.Interaction, course_id: int = None, module_id: int = None, lesson_id: int = None):
    """🎯 Take a quiz for a lesson or module"""
    
    if all([course_id, module_id, lesson_id]):
        # Specific lesson quiz
        await interaction.response.send_message("🎯 Starting quiz...", ephemeral=True)
        await quiz_manager.start_lesson_quiz(interaction.followup, course_id, module_id, lesson_id)
    elif course_id and module_id:
        # Module quiz
        await interaction.response.send_message("🎯 Starting module quiz...", ephemeral=True)
        await quiz_manager.start_module_quiz(interaction.followup, course_id, module_id, interaction.user.id)
    else:
        # Current lesson quiz
        db.add_user(interaction.user.id, interaction.user.display_name)
        user_stats = db.get_user_stats(interaction.user.id)
        if user_stats:
            _, _, _, current_course, current_module, current_lesson = user_stats
            await interaction.response.send_message("🎯 Starting current lesson quiz...", ephemeral=True)
            await quiz_manager.start_lesson_quiz(interaction.followup, current_course, current_module, current_lesson)
        else:
            embed = discord.Embed(
                title="❌ No Current Lesson",
                description="Use `/start` to begin your learning journey first!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="achievements", description="🏆 View your achievements and badges")
async def show_achievements(interaction: discord.Interaction, user: discord.Member = None):
    """🏆 View your achievements and badges"""
    
    target_user = user or interaction.user
    
    # Add user to database
    db.add_user(target_user.id, target_user.display_name)
    
    embed = achievement_manager.create_achievements_list_embed(target_user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="stats", description="📊 View quiz statistics")
async def quiz_stats(interaction: discord.Interaction, user: discord.Member = None):
    """📊 View quiz statistics"""
    
    target_user = user or interaction.user
    await interaction.response.send_message("📊 Loading quiz statistics...", ephemeral=True)
    await quiz_manager.get_quiz_stats(interaction.followup, target_user.id)

@bot.tree.command(name="help", description="❓ Get help with bot commands")
async def help_command(interaction: discord.Interaction):
    """❓ Get help with bot commands"""
    
    embed = discord.Embed(
        title="🤖 Cyber Academy Bot Help",
        description="Your interactive cybersecurity learning companion!",
        color=0x0099FF
    )
    
    embed.add_field(
        name="🚀 Getting Started",
        value="`/start` - Begin your cybersecurity journey\n`/courses` - Browse available courses\n`/lesson` - View your current lesson",
        inline=False
    )
    
    embed.add_field(
        name="📚 Learning Commands",
        value="`/lesson [course] [module] [lesson]` - View specific lesson\n`/quiz` - Take a quiz\n`/quiz [course] [module]` - Take module quiz",
        inline=False
    )
    
    embed.add_field(
        name="📊 Progress Tracking",
        value="`/progress` - Check your progress\n`/achievements` - View your badges\n`/stats` - Quiz statistics\n`/leaderboard` - Top learners",
        inline=False
    )
    
    embed.add_field(
        name="🚩 Advanced Features",
        value="`/ctf` - CTF challenges (500+ XP required)\n`/ctf_leaderboard` - CTF rankings\n`/multimedia [type]` - Interactive content\n`/xp_gates` - View feature unlock requirements",
        inline=False
    )
    
    embed.add_field(
        name="🎬 Multimedia Content",
        value="`/multimedia phishing` - Phishing detection training\n`/multimedia passwords` - Password security visuals\n`/multimedia network` - Network diagrams",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value="`/admin` - Admin control panel (admins only)\n`/admin_award @user achievement` - Award achievement\n`/admin_xp @user amount` - Award XP",
        inline=False
    )
    
    embed.set_footer(text="Need more help? Ask in the community channels!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Add admin commands (will be added when bot starts)
async def setup_cogs():
    await bot.add_cog(AdminCommands(bot))

@bot.event
async def setup_hook():
    await setup_cogs()

# Error handling
# CTF Commands
@bot.tree.command(name="ctf", description="🚩 Access CTF (Capture The Flag) challenges")
async def ctf_command(interaction: discord.Interaction, challenge_id: int = None):
    """CTF challenge system for advanced users"""
    user_id = interaction.user.id
    
    # Register user if not exists
    db.add_user(user_id, interaction.user.display_name)
    
    # Get user stats to check XP requirements
    user_stats = db.get_user_stats(user_id)
    if not user_stats:
        await interaction.response.send_message("❌ Error getting user data.", ephemeral=True)
        return
    
    username, xp, level, current_course, current_module, current_lesson = user_stats
    
    if challenge_id:
        # Show specific challenge
        challenges = ctf_manager.get_available_challenges(xp)
        challenge = next((c for c in challenges if c[0] == challenge_id), None)
        
        if not challenge:
            embed = discord.Embed(
                title="❌ Challenge Not Available",
                description="This challenge doesn't exist or you don't have enough XP to access it.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed, challenge_data = ctf_manager.create_challenge_embed(challenge)
        view = CTFChallengeView(challenge_data, user_id)
        await interaction.response.send_message(embed=embed, view=view)
    
    else:
        # Show available challenges
        challenges = ctf_manager.get_available_challenges(xp)
        
        if not challenges:
            embed = discord.Embed(
                title="🚩 CTF Challenges",
                description=f"No challenges available yet. You need at least 500 XP to access CTF challenges.\n\nYour current XP: **{xp}**",
                color=0xFF8000
            )
            embed.add_field(
                name="How to unlock CTF challenges",
                value="• Complete more lessons to earn XP\n• Take quizzes to boost your score\n• CTF challenges unlock at different XP levels",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="🚩 Available CTF Challenges",
            description=f"Choose a challenge to test your skills! Your XP: **{xp}**",
            color=0x0099FF
        )
        
        challenge_list = ""
        for challenge_id, name, category, difficulty, points, description, required_xp in challenges[:10]:
            challenge_list += f"**{challenge_id}.** {name}\n"
            challenge_list += f"   📂 {category.title()} • {difficulty} • {points} XP\n"
            challenge_list += f"   *{description[:60]}...*\n\n"
        
        embed.add_field(
            name="Challenges",
            value=challenge_list,
            inline=False
        )
        
        embed.add_field(
            name="How to start",
            value="Use `/ctf <challenge_id>` to start a specific challenge",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ctf_leaderboard", description="🏆 View CTF challenge leaderboard")
async def ctf_leaderboard_command(interaction: discord.Interaction):
    """Show CTF leaderboard"""
    embed = ctf_manager.create_leaderboard_embed()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multimedia", description="🎬 Access interactive multimedia content")
async def multimedia_command(interaction: discord.Interaction, content_type: str = "phishing"):
    """Access multimedia learning content"""
    user_id = interaction.user.id
    
    # Register user if not exists
    db.add_user(user_id, interaction.user.display_name)
    
    valid_types = ["phishing", "passwords", "network", "malware", "videos", "audio"]
    if content_type not in valid_types:
        embed = discord.Embed(
            title="❌ Invalid Content Type",
            description=f"Available content types: {', '.join(valid_types)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed, view = multimedia_manager.create_multimedia_embed(content_type, user_id)
    
    if view:
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="xp_gates", description="🔒 View XP requirements for unlocking features")
async def xp_gates_command(interaction: discord.Interaction):
    """Show XP requirements for different features"""
    user_id = interaction.user.id
    
    # Register user if not exists
    db.add_user(user_id, interaction.user.display_name)
    
    # Get user stats
    user_stats = db.get_user_stats(user_id)
    if not user_stats:
        await interaction.response.send_message("❌ Error getting user data.", ephemeral=True)
        return
    
    username, xp, level, current_course, current_module, current_lesson = user_stats
    
    embed = discord.Embed(
        title="🔒 XP Gates & Feature Unlocks",
        description=f"Your current XP: **{xp:,}** • Level **{level}**",
        color=0x0099FF
    )
    
    # Define XP gates
    xp_gates = [
        (0, "🚀 Basic Learning", "Access to all basic courses and lessons"),
        (500, "🚩 CTF Challenges", "Access to beginner CTF challenges"),
        (1000, "🎬 Advanced Multimedia", "Access to advanced interactive content"),
        (1500, "🏆 Expert CTF", "Access to expert-level CTF challenges"),
        (2500, "👑 Master Content", "Access to master-level courses and challenges"),
        (5000, "💎 Elite Features", "Access to exclusive elite content"),
        (10000, "⚡ Legend Status", "All features unlocked + special privileges")
    ]
    
    unlocked = []
    locked = []
    
    for required_xp, feature, description in xp_gates:
        if xp >= required_xp:
            unlocked.append(f"✅ **{feature}** - {description}")
        else:
            remaining = required_xp - xp
            locked.append(f"🔒 **{feature}** - {description}\n   *Need {remaining:,} more XP*")
    
    if unlocked:
        embed.add_field(
            name="🔓 Unlocked Features",
            value="\n\n".join(unlocked),
            inline=False
        )
    
    if locked:
        embed.add_field(
            name="🔒 Locked Features",
            value="\n\n".join(locked),
            inline=False
        )
    
    embed.add_field(
        name="💡 How to Earn XP",
        value="• Complete lessons (+100-250 XP)\n• Take quizzes (+50-150 XP)\n• Solve CTF challenges (+100-600 XP)\n• Earn achievements (bonus XP)",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Arguments",
            description=f"Missing required arguments. Use `/help` for command usage.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Arguments",
            description="Invalid arguments provided. Check your command and try again.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    else:
        print(f"Unhandled error: {error}")
        embed = discord.Embed(
            title="❌ Error",
            description="An unexpected error occurred. Please try again later.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    if not TOKEN:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please create a .env file with your bot token or set the environment variable.")
        exit(1)
    
    print("🔄 Starting Discord bot...")
    print(f"🤖 Bot configured with prefix: {PREFIX}")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Error: Invalid bot token! Please check your .env file.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

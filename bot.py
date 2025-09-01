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
from courses import get_course, get_lesson, get_next_lesson, get_course_list
from achievements import achievement_manager
from quiz import quiz_manager
from admin import AdminCommands

# Bot configuration
PREFIX = "!"
GUILD_ID = 1394809146036977795  # Replace with your server ID

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
            await interaction.response.send_message(
                "❌ This isn't your lesson! Use `!start` to begin your own journey.",
                ephemeral=True
            )
            return
        
        # Get lesson data
        lesson = get_lesson(self.course_id, self.module_id, self.lesson_id)
        if not lesson:
            await interaction.response.send_message("❌ Lesson not found.", ephemeral=True)
            return
        
        # Add user to database if not exists
        db.add_user(interaction.user.id, interaction.user.display_name)
        
        # Award XP
        xp_reward = lesson.get("xp_reward", 100)
        new_xp = db.add_xp(interaction.user.id, xp_reward)
        
        # Update progress
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
        
        # Check for next lesson
        next_lesson_info = get_next_lesson(self.course_id, self.module_id, self.lesson_id)
        if next_lesson_info:
            next_course_id, next_module_id, next_lesson_id = next_lesson_info
            embed.add_field(
                name="What's Next?",
                value=f"Use `!lesson {next_course_id} {next_module_id} {next_lesson_id}` for your next lesson!",
                inline=False
            )
        else:
            embed.add_field(
                name="🎓 Congratulations!",
                value="You've completed all available lessons! More content coming soon.",
                inline=False
            )
        
        # Disable the button
        button.disabled = True
        button.label = "✅ Completed"
        
        await interaction.response.edit_message(embed=embed, view=self)
        
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
            await interaction.response.send_message(
                "❌ This isn't your lesson! Use `!start` to begin your own journey.",
                ephemeral=True
            )
            return
        
        # Check if lesson has a quiz
        lesson = get_lesson(self.course_id, self.module_id, self.lesson_id)
        if not lesson or "quiz" not in lesson:
            await interaction.response.send_message(
                "❌ This lesson doesn't have a quiz available.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "🎯 Starting quiz... Check the new message below!",
            ephemeral=True
        )
        
        # Start the quiz
        await quiz_manager.start_lesson_quiz(
            interaction.followup, self.course_id, self.module_id, self.lesson_id
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

@bot.command(name="start")
async def start_journey(ctx):
    """🚀 Start your cybersecurity learning journey!"""
    
    # Add user to database
    db.add_user(ctx.author.id, ctx.author.display_name)
    
    # Get user stats
    user_stats = db.get_user_stats(ctx.author.id)
    if user_stats:
        username, xp, level, current_course, current_module, current_lesson = user_stats
    else:
        current_course, current_module, current_lesson = 1, 1, 1
        xp, level = 0, 1
    
    # Get current lesson
    lesson = get_lesson(current_course, current_module, current_lesson)
    course = get_course(current_course)
    
    if not lesson or not course:
        embed = discord.Embed(
            title="❌ Error",
            description="Could not find your current lesson. Please contact an administrator.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    
    # Create welcome embed
    embed = discord.Embed(
        title="🚀 Welcome to Cyber Academy!",
        description=f"Ready to continue your cybersecurity journey, **{ctx.author.display_name}**?",
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
        value="• `!lesson` - View current lesson\n• `!courses` - Browse all courses\n• `!progress` - Check your progress\n• `!leaderboard` - See top learners",
        inline=False
    )
    
    embed.set_footer(text="Click the button below to start your next lesson!")
    
    # Create start button
    view = View(timeout=300)
    
    async def start_lesson(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                "❌ This isn't your journey! Use `!start` to begin your own.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"📖 Loading lesson: **{lesson['title']}**...",
            ephemeral=True
        )
        
        # Show the lesson
        await show_lesson(ctx, current_course, current_module, current_lesson)
    
    start_button = Button(label="📖 Start Next Lesson", style=discord.ButtonStyle.green)
    start_button.callback = start_lesson
    view.add_item(start_button)
    
    await ctx.send(embed=embed, view=view)

@bot.command(name="lesson")
async def show_lesson(ctx, course_id: int = None, module_id: int = None, lesson_id: int = None):
    """📖 View a specific lesson or your current lesson"""
    
    # Add user to database
    db.add_user(ctx.author.id, ctx.author.display_name)
    
    # If no parameters provided, show current lesson
    if not all([course_id, module_id, lesson_id]):
        user_stats = db.get_user_stats(ctx.author.id)
        if user_stats:
            _, _, _, course_id, module_id, lesson_id = user_stats
        else:
            course_id, module_id, lesson_id = 1, 1, 1
    
    # Get lesson and course data
    lesson = get_lesson(course_id, module_id, lesson_id)
    course = get_course(course_id)
    
    if not lesson:
        embed = discord.Embed(
            title="❌ Lesson Not Found",
            description="Could not find the specified lesson.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
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
    
    embed.set_footer(text="Complete the lesson to earn XP and unlock achievements!")
    
    # Create lesson view with buttons
    view = LessonView(ctx.author.id, course_id, module_id, lesson_id)
    
    await ctx.send(embed=embed, view=view)

@bot.command(name="courses")
async def list_courses(ctx):
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
            value=f"{course['description']}\nUse `!lesson {course['id']} 1 1` to start",
            inline=False
        )
    
    embed.set_footer(text="More courses coming soon!")
    
    await ctx.send(embed=embed)

@bot.command(name="progress")
async def show_progress(ctx, user: discord.Member = None):
    """📊 Check your learning progress"""
    
    target_user = user or ctx.author
    
    # Add user to database
    db.add_user(target_user.id, target_user.display_name)
    
    user_stats = db.get_user_stats(target_user.id)
    if not user_stats:
        embed = discord.Embed(
            title="❌ No Progress Found",
            description="Start learning with `!start` to track your progress!",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
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
    
    await ctx.send(embed=embed)

@bot.command(name="leaderboard", aliases=["lb", "top"])
async def show_leaderboard(ctx):
    """🏆 View the top cybersecurity learners"""
    
    leaderboard = db.get_leaderboard(10)
    
    if not leaderboard:
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="No learners yet! Be the first to start your cybersecurity journey!",
            color=0xFFD700
        )
        await ctx.send(embed=embed)
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
    
    await ctx.send(embed=embed)

@bot.command(name="quiz")
async def start_quiz(ctx, course_id: int = None, module_id: int = None, lesson_id: int = None):
    """🎯 Take a quiz for a lesson or module"""
    
    if all([course_id, module_id, lesson_id]):
        # Specific lesson quiz
        await quiz_manager.start_lesson_quiz(ctx, course_id, module_id, lesson_id)
    elif course_id and module_id:
        # Module quiz
        await quiz_manager.start_module_quiz(ctx, course_id, module_id)
    else:
        # Current lesson quiz
        db.add_user(ctx.author.id, ctx.author.display_name)
        user_stats = db.get_user_stats(ctx.author.id)
        if user_stats:
            _, _, _, current_course, current_module, current_lesson = user_stats
            await quiz_manager.start_lesson_quiz(ctx, current_course, current_module, current_lesson)
        else:
            embed = discord.Embed(
                title="❌ No Current Lesson",
                description="Use `!start` to begin your learning journey first!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

@bot.command(name="achievements", aliases=["ach", "badges"])
async def show_achievements(ctx, user: discord.Member = None):
    """🏆 View your achievements and badges"""
    
    target_user = user or ctx.author
    
    # Add user to database
    db.add_user(target_user.id, target_user.display_name)
    
    embed = achievement_manager.create_achievements_list_embed(target_user.id)
    await ctx.send(embed=embed)

@bot.command(name="stats")
async def quiz_stats(ctx, user: discord.Member = None):
    """📊 View quiz statistics"""
    
    target_user = user or ctx.author
    await quiz_manager.get_quiz_stats(ctx, target_user.id)

@bot.command(name="help_cyber", aliases=["help_academy"])
async def help_command(ctx):
    """❓ Get help with bot commands"""
    
    embed = discord.Embed(
        title="🤖 Cyber Academy Bot Help",
        description="Your interactive cybersecurity learning companion!",
        color=0x0099FF
    )
    
    embed.add_field(
        name="🚀 Getting Started",
        value="`!start` - Begin your cybersecurity journey\n`!courses` - Browse available courses\n`!lesson` - View your current lesson",
        inline=False
    )
    
    embed.add_field(
        name="📚 Learning Commands",
        value="`!lesson [course] [module] [lesson]` - View specific lesson\n`!quiz` - Take a quiz\n`!quiz [course] [module]` - Take module quiz",
        inline=False
    )
    
    embed.add_field(
        name="📊 Progress Tracking",
        value="`!progress` - Check your progress\n`!achievements` - View your badges\n`!stats` - Quiz statistics\n`!leaderboard` - Top learners",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value="`!admin` - Admin control panel (admins only)\n`!admin_award @user achievement` - Award achievement\n`!admin_xp @user amount` - Award XP",
        inline=False
    )
    
    embed.set_footer(text="Need more help? Ask in the community channels!")
    
    await ctx.send(embed=embed)

# Add admin commands (will be added when bot starts)
async def setup_cogs():
    await bot.add_cog(AdminCommands(bot))

@bot.event
async def setup_hook():
    await setup_cogs()

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Arguments",
            description=f"Missing required arguments. Use `!help_cyber` for command usage.",
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

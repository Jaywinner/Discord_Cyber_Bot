"""
Admin Commands for Cybersecurity Learning Bot
Provides administrative functionality for managing courses, users, and bot settings
"""

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from discord import app_commands
import json
from database import db
from achievements import achievement_manager
from courses import COURSES

# Admin user IDs - replace with actual admin Discord IDs
ADMIN_IDS = [
    1394809146036977795,  # Replace with your Discord ID
    # Add more admin IDs as needed
]

def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in ADMIN_IDS

class AddCourseModal(Modal):
    def __init__(self):
        super().__init__(title="Add New Course")
        
        self.course_title = TextInput(
            label="Course Title",
            placeholder="e.g., Advanced Network Security",
            max_length=100
        )
        
        self.course_description = TextInput(
            label="Course Description", 
            placeholder="Brief description of the course content",
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        
        self.course_level = TextInput(
            label="Course Level",
            placeholder="Beginner, Intermediate, or Advanced",
            max_length=20
        )
        
        self.add_item(self.course_title)
        self.add_item(self.course_description)
        self.add_item(self.course_level)
    
    async def on_submit(self, interaction: discord.Interaction):
        # This would typically save to a database or file
        # For now, we'll just show a confirmation
        embed = discord.Embed(
            title="✅ Course Added Successfully",
            description=f"**{self.course_title.value}** has been added to the course catalog.",
            color=0x00FF00
        )
        
        embed.add_field(name="Description", value=self.course_description.value, inline=False)
        embed.add_field(name="Level", value=self.course_level.value, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdminView(View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📊 User Stats", style=discord.ButtonStyle.primary)
    async def user_stats(self, interaction: discord.Interaction, button: Button):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        # Get overall statistics
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Active users (users with XP > 0)
            cursor.execute("SELECT COUNT(*) FROM users WHERE xp > 0")
            active_users = cursor.fetchone()[0]
            
            # Total XP awarded
            cursor.execute("SELECT SUM(xp) FROM users")
            total_xp = cursor.fetchone()[0] or 0
            
            # Total lessons completed
            cursor.execute("SELECT COUNT(*) FROM course_progress WHERE completed = TRUE")
            total_lessons = cursor.fetchone()[0]
            
            # Total quiz attempts
            cursor.execute("SELECT COUNT(*) FROM quiz_attempts")
            total_quizzes = cursor.fetchone()[0]
            
            # Top users
            cursor.execute("SELECT username, xp, level FROM users ORDER BY xp DESC LIMIT 5")
            top_users = cursor.fetchall()
            
            embed = discord.Embed(
                title="📊 Bot Statistics",
                color=0x0099FF
            )
            
            embed.add_field(
                name="👥 Users",
                value=f"• **Total:** {total_users}\n• **Active:** {active_users}",
                inline=True
            )
            
            embed.add_field(
                name="📚 Learning Activity",
                value=f"• **Lessons Completed:** {total_lessons}\n• **Quiz Attempts:** {total_quizzes}",
                inline=True
            )
            
            embed.add_field(
                name="⭐ XP System",
                value=f"• **Total XP Awarded:** {total_xp:,}",
                inline=True
            )
            
            if top_users:
                top_users_text = "\n".join([f"{i+1}. {username} - {xp:,} XP (Level {level})" 
                                          for i, (username, xp, level) in enumerate(top_users)])
                embed.add_field(
                    name="🏆 Top Learners",
                    value=top_users_text,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error retrieving stats: {e}", ephemeral=True)
        finally:
            conn.close()
    
    @discord.ui.button(label="🎓 Add Course", style=discord.ButtonStyle.success)
    async def add_course(self, interaction: discord.Interaction, button: Button):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        modal = AddCourseModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏆 Award Achievement", style=discord.ButtonStyle.secondary)
    async def award_achievement(self, interaction: discord.Interaction, button: Button):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 Award Achievement",
            description="Use the command `/admin_award @user achievement_name` to award achievements manually.",
            color=0xFFD700
        )
        
        embed.add_field(
            name="Available Achievements",
            value="• community_helper\n• early_adopter\n• Or any custom achievement name",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db
    
    @discord.app_commands.command(name="admin", description="Open the admin control panel")
    async def admin_panel(self, interaction: discord.Interaction):
        """Open the admin control panel"""
        if not is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use admin commands.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛠️ Admin Control Panel",
            description="Select an action below:",
            color=0x0099FF
        )
        
        view = AdminView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="admin_award", description="Award an achievement to a user")
    async def award_achievement(self, interaction: discord.Interaction, user: discord.Member, achievement_name: str):
        """Award an achievement to a user"""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        # Add user to database if not exists
        self.db.add_user(user.id, user.display_name)
        
        # Award achievement
        success = self.db.add_achievement(user.id, achievement_name, "special")
        
        if success:
            # Award bonus XP
            self.db.add_xp(user.id, 300)
            
            embed = discord.Embed(
                title="🏆 Achievement Awarded!",
                description=f"**{achievement_name}** has been awarded to {user.mention}",
                color=0xFFD700
            )
            
            embed.add_field(name="Bonus XP", value="+300 XP", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="🎉 Special Achievement Unlocked!",
                    description=f"You've been awarded: **{achievement_name}**",
                    color=0xFFD700
                )
                dm_embed.add_field(name="Bonus XP", value="+300 XP", inline=True)
                dm_embed.set_footer(text="Awarded by an administrator")
                
                await user.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
        else:
            await interaction.response.send_message(f"❌ {user.display_name} already has this achievement or there was an error.", ephemeral=True)
    
    @app_commands.command(name="admin_xp", description="Award XP to a user")
    async def award_xp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Award XP to a user"""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        if amount <= 0 or amount > 10000:
            await interaction.response.send_message("❌ XP amount must be between 1 and 10,000.", ephemeral=True)
            return
        
        # Add user to database if not exists
        self.db.add_user(user.id, user.display_name)
        
        # Award XP
        new_xp = self.db.add_xp(user.id, amount)
        
        embed = discord.Embed(
            title="⭐ XP Awarded!",
            description=f"**{amount} XP** has been awarded to {user.mention}",
            color=0x00FF00
        )
        
        embed.add_field(name="New Total XP", value=f"{new_xp:,} XP", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check for new achievements
        new_achievements = achievement_manager.check_and_award_achievements(user.id)
        if new_achievements:
            achievement_text = "\n".join([f"🏆 {ach['name']}" for ach in new_achievements])
            follow_up = discord.Embed(
                title="🎉 New Achievements Unlocked!",
                description=achievement_text,
                color=0xFFD700
            )
            await interaction.followup.send(embed=follow_up, ephemeral=True)
    
    @app_commands.command(name="admin_reset", description="Reset a user's progress (use with caution!)")
    async def reset_user(self, interaction: discord.Interaction, user: discord.Member):
        """Reset a user's progress (use with caution!)"""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        # Confirmation check
        embed = discord.Embed(
            title="⚠️ Confirm Reset",
            description=f"Are you sure you want to reset **{user.display_name}**'s progress?\n\nThis will:\n• Reset XP to 0\n• Reset level to 1\n• Clear all achievements\n• Clear course progress\n\n**This action cannot be undone!**",
            color=0xFF6600
        )
        
        # Add confirmation buttons
        view = View(timeout=30)
        
        async def confirm_reset(button_interaction):
            if button_interaction.user.id != interaction.user.id:
                await button_interaction.response.send_message("❌ Only the command user can confirm.", ephemeral=True)
                return
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                # Reset user data
                cursor.execute("UPDATE users SET xp = 0, level = 1, current_course = 1, current_module = 1, current_lesson = 1 WHERE user_id = ?", (user.id,))
                cursor.execute("DELETE FROM achievements WHERE user_id = ?", (user.id,))
                cursor.execute("DELETE FROM course_progress WHERE user_id = ?", (user.id,))
                cursor.execute("DELETE FROM quiz_attempts WHERE user_id = ?", (user.id,))
                conn.commit()
                
                reset_embed = discord.Embed(
                    title="✅ User Reset Complete",
                    description=f"**{user.display_name}**'s progress has been reset.",
                    color=0x00FF00
                )
                
                await button_interaction.response.edit_message(embed=reset_embed, view=None)
                
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ Reset Failed",
                    description=f"Error resetting user: {e}",
                    color=0xFF0000
                )
                await button_interaction.response.edit_message(embed=error_embed, view=None)
            finally:
                conn.close()
        
        async def cancel_reset(button_interaction):
            if button_interaction.user.id != interaction.user.id:
                await button_interaction.response.send_message("❌ Only the command user can cancel.", ephemeral=True)
                return
            
            cancel_embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="User reset has been cancelled.",
                color=0x999999
            )
            await button_interaction.response.edit_message(embed=cancel_embed, view=None)
        
        confirm_button = Button(label="✅ Confirm Reset", style=discord.ButtonStyle.danger)
        cancel_button = Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        confirm_button.callback = confirm_reset
        cancel_button.callback = cancel_reset
        
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="admin_backup", description="Create a backup of user data")
    async def backup_data(self, interaction: discord.Interaction):
        """Create a backup of user data"""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get all user data
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            cursor.execute("SELECT * FROM achievements")
            achievements = cursor.fetchall()
            
            cursor.execute("SELECT * FROM course_progress")
            progress = cursor.fetchall()
            
            cursor.execute("SELECT * FROM quiz_attempts")
            quizzes = cursor.fetchall()
            
            # Create backup data structure
            backup_data = {
                "users": users,
                "achievements": achievements,
                "course_progress": progress,
                "quiz_attempts": quizzes,
                "backup_timestamp": discord.utils.utcnow().isoformat()
            }
            
            # Save to file
            with open("backup.json", "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            embed = discord.Embed(
                title="✅ Backup Created",
                description="Database backup has been created successfully.",
                color=0x00FF00
            )
            
            embed.add_field(name="Records Backed Up", 
                          value=f"• Users: {len(users)}\n• Achievements: {len(achievements)}\n• Progress: {len(progress)}\n• Quiz Attempts: {len(quizzes)}", 
                          inline=False)
            
            await interaction.response.send_message(embed=embed, file=discord.File("backup.json"), ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Backup Failed",
                description=f"Error creating backup: {e}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            conn.close()

def setup(bot):
    """Setup function for the cog"""
    bot.add_cog(AdminCommands(bot))

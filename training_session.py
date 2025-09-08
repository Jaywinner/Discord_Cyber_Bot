"""
Training Session Manager
Handles stop/resume functionality for learning sessions
"""

import discord
from discord.ui import Button, View
import json
from datetime import datetime
from database import db

class TrainingSessionManager:
    """Manages training sessions with stop/resume functionality"""
    
    def __init__(self):
        self.active_sessions = {}  # user_id: session_data
    
    def save_session(self, user_id: int, session_type: str, current_position: dict, session_data: dict):
        """Save a training session to database"""
        position_json = json.dumps(current_position)
        data_json = json.dumps(session_data)
        
        return db.save_training_session(user_id, session_type, position_json, data_json)
    
    def load_session(self, user_id: int, session_type: str):
        """Load a training session from database"""
        session = db.get_training_session(user_id, session_type)
        
        if session:
            position_str, data_str, paused_at = session
            try:
                position = json.loads(position_str) if position_str else {}
                data = json.loads(data_str) if data_str else {}
                return position, data, paused_at
            except json.JSONDecodeError:
                return None, None, None
        
        return None, None, None
    
    def delete_session(self, user_id: int, session_type: str):
        """Delete a completed training session"""
        return db.delete_training_session(user_id, session_type)
    
    def get_user_sessions(self, user_id: int):
        """Get all saved sessions for a user"""
        sessions = db.get_user_training_sessions(user_id)
        formatted_sessions = []
        
        for session_type, position_str, paused_at in sessions:
            try:
                position = json.loads(position_str) if position_str else {}
                formatted_sessions.append({
                    'type': session_type,
                    'position': position,
                    'paused_at': paused_at
                })
            except json.JSONDecodeError:
                continue
        
        return formatted_sessions
    
    def create_session_embed(self, user_id: int):
        """Create embed showing saved sessions"""
        sessions = self.get_user_sessions(user_id)
        
        embed = discord.Embed(
            title="📚 Your Saved Training Sessions",
            description="Resume your learning from where you left off!",
            color=0x0099FF
        )
        
        if not sessions:
            embed.add_field(
                name="No Saved Sessions",
                value="You don't have any paused training sessions. Start a lesson, quiz, or CTF challenge to create a session!",
                inline=False
            )
            return embed, None
        
        session_list = ""
        for i, session in enumerate(sessions[:5], 1):  # Limit to 5 sessions
            session_type = session['type'].title()
            paused_at = session['paused_at']
            
            # Format position info based on session type
            position_info = ""
            if session['type'] == 'lesson':
                pos = session['position']
                position_info = f"Course {pos.get('course', '?')}, Module {pos.get('module', '?')}, Lesson {pos.get('lesson', '?')}"
            elif session['type'] == 'quiz':
                pos = session['position']
                position_info = f"Question {pos.get('current_question', '?')} of {pos.get('total_questions', '?')}"
            elif session['type'] == 'ctf':
                pos = session['position']
                position_info = f"Challenge: {pos.get('challenge_name', 'Unknown')}"
            elif session['type'] == 'multimedia':
                pos = session['position']
                position_info = f"Content: {pos.get('content_type', 'Unknown')}"
            
            session_list += f"**{i}.** {session_type} Session\n"
            session_list += f"   📍 {position_info}\n"
            session_list += f"   ⏰ Paused: {paused_at[:16]}\n\n"
        
        embed.add_field(
            name="Saved Sessions",
            value=session_list,
            inline=False
        )
        
        embed.add_field(
            name="How to Resume",
            value="Use the buttons below to resume a session, or use:\n• `/lesson` - Resume lesson\n• `/quiz` - Resume quiz\n• `/ctf` - Resume CTF\n• `/multimedia` - Resume multimedia",
            inline=False
        )
        
        # Create view with resume buttons
        view = TrainingSessionView(user_id, sessions[:5])
        return embed, view

class TrainingSessionView(View):
    """View for managing training sessions"""
    
    def __init__(self, user_id: int, sessions: list):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.sessions = sessions
        
        # Add resume buttons for each session
        for i, session in enumerate(sessions):
            button = Button(
                label=f"Resume {session['type'].title()}",
                style=discord.ButtonStyle.primary,
                custom_id=f"resume_{session['type']}_{i}",
                emoji="▶️"
            )
            button.callback = self.create_resume_callback(session)
            self.add_item(button)
        
        # Add clear all button
        if sessions:
            clear_button = Button(
                label="Clear All Sessions",
                style=discord.ButtonStyle.danger,
                custom_id="clear_all",
                emoji="🗑️"
            )
            clear_button.callback = self.clear_all_sessions
            self.add_item(clear_button)
    
    def create_resume_callback(self, session):
        """Create callback for resume button"""
        async def resume_callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This is not your session!", ephemeral=True)
                return
            
            session_type = session['type']
            position = session['position']
            
            # Create resume message based on session type
            embed = discord.Embed(
                title=f"▶️ Resuming {session_type.title()} Session",
                description=f"Continuing from where you left off...",
                color=0x00FF00
            )
            
            if session_type == 'lesson':
                embed.add_field(
                    name="Resuming Lesson",
                    value=f"Course {position.get('course', '?')}, Module {position.get('module', '?')}, Lesson {position.get('lesson', '?')}",
                    inline=False
                )
                embed.add_field(
                    name="Next Steps",
                    value="Use `/lesson` command to continue your lesson",
                    inline=False
                )
            elif session_type == 'quiz':
                embed.add_field(
                    name="Resuming Quiz",
                    value=f"Question {position.get('current_question', '?')} of {position.get('total_questions', '?')}",
                    inline=False
                )
                embed.add_field(
                    name="Next Steps",
                    value="Use `/quiz` command to continue your quiz",
                    inline=False
                )
            elif session_type == 'ctf':
                embed.add_field(
                    name="Resuming CTF Challenge",
                    value=f"Challenge: {position.get('challenge_name', 'Unknown')}",
                    inline=False
                )
                embed.add_field(
                    name="Next Steps",
                    value=f"Use `/ctf {position.get('challenge_id', '')}` to continue",
                    inline=False
                )
            elif session_type == 'multimedia':
                embed.add_field(
                    name="Resuming Multimedia Content",
                    value=f"Content: {position.get('content_type', 'Unknown')}",
                    inline=False
                )
                embed.add_field(
                    name="Next Steps",
                    value=f"Use `/multimedia {position.get('content_type', '')}` to continue",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        return resume_callback
    
    async def clear_all_sessions(self, interaction: discord.Interaction):
        """Clear all saved sessions"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your session!", ephemeral=True)
            return
        
        # Delete all sessions for this user
        for session in self.sessions:
            db.delete_training_session(self.user_id, session['type'])
        
        embed = discord.Embed(
            title="🗑️ Sessions Cleared",
            description="All your saved training sessions have been cleared.",
            color=0xFF8000
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class StopResumeView(View):
    """View with Stop and Continue buttons for active training"""
    
    def __init__(self, user_id: int, session_type: str, current_position: dict, session_data: dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.session_type = session_type
        self.current_position = current_position
        self.session_data = session_data
    
    @discord.ui.button(label="⏸️ Stop & Save", style=discord.ButtonStyle.secondary)
    async def stop_session(self, interaction: discord.Interaction, button: Button):
        """Stop and save current session"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your session!", ephemeral=True)
            return
        
        # Save session to database
        success = training_session_manager.save_session(
            self.user_id, 
            self.session_type, 
            self.current_position, 
            self.session_data
        )
        
        if success:
            embed = discord.Embed(
                title="⏸️ Session Saved",
                description=f"Your {self.session_type} session has been saved. You can resume it later using `/sessions` or the specific command.",
                color=0x00FF00
            )
            embed.add_field(
                name="How to Resume",
                value=f"• Use `/sessions` to see all saved sessions\n• Use `/{self.session_type}` to resume directly",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Save Failed",
                description="Failed to save your session. Please try again.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="▶️ Continue", style=discord.ButtonStyle.primary)
    async def continue_session(self, interaction: discord.Interaction, button: Button):
        """Continue with current session"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your session!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="▶️ Continuing Session",
            description=f"Continuing with your {self.session_type} session...",
            color=0x0099FF
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Global training session manager instance
training_session_manager = TrainingSessionManager()
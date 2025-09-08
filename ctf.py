"""
CTF (Capture The Flag) Challenge System
Advanced cybersecurity challenges for experienced users
"""

import discord
from discord.ui import Button, View, Modal, TextInput
import random
from database import db
from achievements import achievement_manager

# CTF Challenge Categories
CTF_CATEGORIES = {
    "web": "🌐 Web Security",
    "crypto": "🔐 Cryptography", 
    "forensics": "🔍 Digital Forensics",
    "reverse": "⚙️ Reverse Engineering",
    "pwn": "💥 Binary Exploitation",
    "osint": "🕵️ Open Source Intelligence",
    "steganography": "🖼️ Steganography",
    "network": "🌐 Network Security"
}

# Predefined CTF Challenges
CTF_CHALLENGES = [
    {
        "name": "Basic Base64",
        "category": "crypto",
        "difficulty": "Easy",
        "points": 100,
        "description": "Decode this Base64 string: `Q3liZXJTZWN1cml0eUJvdA==`",
        "flag": "CyberSecurityBot",
        "hints": "Base64 is a common encoding method. Try using an online decoder or command line tools.",
        "required_xp": 500
    },
    {
        "name": "Caesar's Secret",
        "category": "crypto", 
        "difficulty": "Easy",
        "points": 150,
        "description": "Julius Caesar used this cipher: `FBOHU{FDHVDU_FLSKHU_LV_HDV}`",
        "flag": "CYBER{CAESAR_CIPHER_IS_EAS}",
        "hints": "Caesar cipher shifts letters by a fixed number. Try different shift values.",
        "required_xp": 750
    },
    {
        "name": "Hidden in Plain Sight",
        "category": "steganography",
        "difficulty": "Medium", 
        "points": 200,
        "description": "Look carefully at this text: `The flag is hidden in Every Very Easy Riddle You Tackle Here In New Games`",
        "flag": "EVERYTHING",
        "hints": "Sometimes the answer is in the first letter of each word.",
        "required_xp": 1000
    },
    {
        "name": "SQL Injection Basics",
        "category": "web",
        "difficulty": "Medium",
        "points": 250,
        "description": "What SQL injection payload would bypass this login? `SELECT * FROM users WHERE username='$input' AND password='$pass'`",
        "flag": "' OR '1'='1",
        "hints": "Think about how to make the WHERE clause always true.",
        "required_xp": 1200
    },
    {
        "name": "Network Detective",
        "category": "network",
        "difficulty": "Medium",
        "points": 300,
        "description": "What port is commonly used for HTTPS traffic?",
        "flag": "443",
        "hints": "HTTP uses port 80, but what about its secure version?",
        "required_xp": 800
    },
    {
        "name": "Hash Cracker",
        "category": "crypto",
        "difficulty": "Hard",
        "points": 400,
        "description": "Crack this MD5 hash: `5d41402abc4b2a76b9719d911017c592`",
        "flag": "hello",
        "hints": "This is a common word. Try a dictionary attack or online hash crackers.",
        "required_xp": 1500
    },
    {
        "name": "OSINT Investigation",
        "category": "osint",
        "difficulty": "Hard",
        "points": 500,
        "description": "What is the most common password used in data breaches according to security reports?",
        "flag": "123456",
        "hints": "Look up recent security reports about the most common passwords.",
        "required_xp": 2000
    },
    {
        "name": "Binary Puzzle",
        "category": "reverse",
        "difficulty": "Expert",
        "points": 600,
        "description": "Convert this binary to ASCII: `01000011 01011001 01000010 01000101 01010010`",
        "flag": "CYBER",
        "hints": "Each 8-bit binary number represents one ASCII character.",
        "required_xp": 2500
    }
]

class CTFSubmissionModal(Modal):
    def __init__(self, challenge_id: int, challenge_name: str):
        super().__init__(title=f"Submit Flag: {challenge_name}")
        self.challenge_id = challenge_id
        
        self.flag_input = TextInput(
            label="Flag",
            placeholder="Enter your flag here...",
            required=True,
            max_length=200
        )
        self.add_item(self.flag_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        submitted_flag = self.flag_input.value.strip()
        
        # Submit flag to database
        is_correct, points = db.submit_ctf_flag(user_id, self.challenge_id, submitted_flag)
        
        if is_correct:
            embed = discord.Embed(
                title="🎉 Correct Flag!",
                description=f"Congratulations! You solved the challenge and earned **{points} XP**!",
                color=0x00FF00
            )
            
            # Check for achievements
            new_achievements = achievement_manager.check_and_award_achievements(user_id, "ctf_solve")
            if new_achievements:
                achievement_text = "\n".join([f"🏆 {ach['name']}" for ach in new_achievements])
                embed.add_field(
                    name="New Achievements!",
                    value=achievement_text,
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="❌ Incorrect Flag",
                description="That's not the correct flag. Keep trying!",
                color=0xFF0000
            )
            embed.add_field(
                name="Hint",
                value="Double-check your answer and try again. Remember that flags are case-sensitive!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CTFChallengeView(View):
    def __init__(self, challenge_data: dict, user_id: int):
        super().__init__(timeout=300)
        self.challenge_data = challenge_data
        self.user_id = user_id
        
        # Add submit flag button
        submit_button = Button(
            label="Submit Flag",
            style=discord.ButtonStyle.primary,
            emoji="🚩"
        )
        submit_button.callback = self.submit_flag
        self.add_item(submit_button)
        
        # Add hint button
        hint_button = Button(
            label="Get Hint",
            style=discord.ButtonStyle.secondary,
            emoji="💡"
        )
        hint_button.callback = self.show_hint
        self.add_item(hint_button)
        
        # Add stop & save button
        stop_button = Button(
            label="⏸️ Stop & Save",
            style=discord.ButtonStyle.danger,
            emoji="⏸️"
        )
        stop_button.callback = self.stop_ctf
        self.add_item(stop_button)
    
    async def submit_flag(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your challenge! Use `/ctf` to start your own.",
                ephemeral=True
            )
            return
        
        modal = CTFSubmissionModal(self.challenge_data['id'], self.challenge_data['name'])
        await interaction.response.send_modal(modal)
    
    async def show_hint(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your challenge!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="💡 Hint",
            description=self.challenge_data.get('hints', 'No hints available for this challenge.'),
            color=0xFFFF00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def stop_ctf(self, interaction: discord.Interaction):
        """Stop and save CTF challenge progress"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your challenge!", ephemeral=True)
            return
        
        # Import here to avoid circular imports
        from training_session import training_session_manager
        from datetime import datetime
        
        # Save CTF session
        current_position = {
            'challenge_id': self.challenge_data['id'],
            'challenge_name': self.challenge_data['name'],
            'category': self.challenge_data['category']
        }
        session_data = {
            'challenge_description': self.challenge_data['description'],
            'difficulty': self.challenge_data['difficulty'],
            'points': self.challenge_data['points'],
            'saved_at': str(datetime.now())
        }
        
        success = training_session_manager.save_session(
            self.user_id, 
            'ctf', 
            current_position, 
            session_data
        )
        
        if success:
            embed = discord.Embed(
                title="⏸️ CTF Challenge Session Saved",
                description=f"Your CTF challenge progress has been saved. Resume anytime with `/ctf {self.challenge_data['id']}` or `/sessions`.",
                color=0x00FF00
            )
            embed.add_field(
                name="Saved Challenge",
                value=f"{self.challenge_data['name']} ({self.challenge_data['category']})",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Save Failed",
                description="Failed to save your CTF challenge session. Please try again.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CTFManager:
    def __init__(self):
        self.initialize_challenges()
    
    def initialize_challenges(self):
        """Initialize CTF challenges in the database"""
        for challenge in CTF_CHALLENGES:
            db.add_ctf_challenge(
                name=challenge['name'],
                category=challenge['category'],
                difficulty=challenge['difficulty'],
                points=challenge['points'],
                description=challenge['description'],
                flag=challenge['flag'],
                hints=challenge['hints'],
                required_xp=challenge['required_xp']
            )
    
    def get_available_challenges(self, user_xp: int):
        """Get challenges available to user based on XP"""
        return db.get_ctf_challenges(user_xp)
    
    def create_challenge_embed(self, challenge_data: tuple):
        """Create Discord embed for a challenge"""
        challenge_id, name, category, difficulty, points, description, required_xp = challenge_data
        
        # Difficulty colors
        difficulty_colors = {
            "Easy": 0x00FF00,
            "Medium": 0xFFFF00,
            "Hard": 0xFF8000,
            "Expert": 0xFF0000
        }
        
        embed = discord.Embed(
            title=f"🚩 {name}",
            description=description,
            color=difficulty_colors.get(difficulty, 0x0099FF)
        )
        
        embed.add_field(
            name="Category",
            value=CTF_CATEGORIES.get(category, category.title()),
            inline=True
        )
        
        embed.add_field(
            name="Difficulty",
            value=f"{difficulty}",
            inline=True
        )
        
        embed.add_field(
            name="Points",
            value=f"{points} XP",
            inline=True
        )
        
        embed.add_field(
            name="Required XP",
            value=f"{required_xp} XP",
            inline=True
        )
        
        embed.set_footer(text="Submit your flag to earn XP and unlock achievements!")
        
        return embed, {"id": challenge_id, "name": name, "hints": self.get_challenge_hints(name)}
    
    def get_challenge_hints(self, challenge_name: str):
        """Get hints for a specific challenge"""
        for challenge in CTF_CHALLENGES:
            if challenge['name'] == challenge_name:
                return challenge['hints']
        return "No hints available."
    
    def get_user_progress(self, user_id: int):
        """Get user's CTF progress"""
        return db.get_user_ctf_progress(user_id)
    
    def create_leaderboard_embed(self):
        """Create CTF leaderboard embed"""
        # Get top CTF solvers
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT u.username, SUM(c.points) as total_points, COUNT(s.id) as challenges_solved
                FROM ctf_submissions s
                JOIN users u ON s.user_id = u.user_id
                JOIN ctf_challenges c ON s.challenge_id = c.id
                WHERE s.is_correct = 1
                GROUP BY u.user_id, u.username
                ORDER BY total_points DESC, challenges_solved DESC
                LIMIT 10
            """)
            
            leaderboard = cursor.fetchall()
            
            embed = discord.Embed(
                title="🏆 CTF Leaderboard",
                description="Top CTF challenge solvers",
                color=0xFFD700
            )
            
            if leaderboard:
                leaderboard_text = ""
                for i, (username, points, solved) in enumerate(leaderboard, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    leaderboard_text += f"{medal} **{username}** - {points} pts ({solved} solved)\n"
                
                embed.add_field(
                    name="Rankings",
                    value=leaderboard_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="No Data",
                    value="No CTF challenges have been solved yet!",
                    inline=False
                )
            
            return embed
        
        except Exception as e:
            print(f"Error creating CTF leaderboard: {e}")
            return discord.Embed(
                title="❌ Error",
                description="Could not load CTF leaderboard.",
                color=0xFF0000
            )
        finally:
            conn.close()

# Global CTF manager instance
ctf_manager = CTFManager()
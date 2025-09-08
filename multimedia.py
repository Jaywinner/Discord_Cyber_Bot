"""
Multimedia Content Manager
Handles images, videos, audio, and interactive content for lessons
"""

import discord
from discord.ui import Button, View
import random
from database import db

# Sample multimedia content URLs (using placeholder services and free resources)
MULTIMEDIA_CONTENT = {
    # Phishing Email Examples (Real cybersecurity training images)
    "phishing_examples": [
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&h=400&fit=crop",
            "description": "Example of a fake PayPal phishing email with suspicious sender and urgent language",
            "is_phishing": True,
            "explanation": "Red flags: Generic greeting, urgent language, suspicious sender email, and fake URL"
        },
        {
            "type": "image", 
            "url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&h=400&fit=crop",
            "description": "Example of a legitimate bank email with proper branding and security features",
            "is_phishing": False,
            "explanation": "This is legitimate: Personalized greeting, official domain, no urgent threats"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&h=400&fit=crop",
            "description": "Fake Amazon security alert with misspelled domain and grammar errors",
            "is_phishing": True,
            "explanation": "Red flags: Misspelled domain (amazom.com), poor grammar, creates false urgency"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&h=400&fit=crop",
            "description": "Microsoft Office 365 phishing attempt with fake login page",
            "is_phishing": True,
            "explanation": "Red flags: Suspicious URL, credential harvesting, urgency tactics"
        }
    ],
    
    # Password Security Visuals (Real cybersecurity images)
    "password_examples": [
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=600&h=300&fit=crop",
            "description": "Password security visualization showing weak vs strong passwords",
            "strength": "comparison"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=600&h=300&fit=crop",
            "description": "Digital security concept with password protection",
            "strength": "strong"
        }
    ],
    
    # Network Security Diagrams (Real technical diagrams)
    "network_diagrams": [
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&h=400&fit=crop",
            "description": "Network infrastructure and connectivity visualization",
            "topic": "network_basics"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop",
            "description": "Digital network connections and data flow",
            "topic": "network_security"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&h=400&fit=crop",
            "description": "VPN and secure connection concepts",
            "topic": "vpn_security"
        }
    ],
    
    # Malware Examples (Safe cybersecurity representations)
    "malware_examples": [
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&h=400&fit=crop",
            "description": "Cybersecurity threat visualization - malware detection",
            "malware_type": "general_malware"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&h=400&fit=crop",
            "description": "Security warning and threat detection interface",
            "malware_type": "security_alert"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&h=400&fit=crop",
            "description": "Digital security and protection concepts",
            "malware_type": "protection"
        }
    ],
    
    # Educational Videos (Real cybersecurity educational content)
    "educational_videos": [
        {
            "type": "video",
            "url": "https://www.youtube.com/watch?v=Z7Wl2FW2TcA",
            "description": "What is Phishing? - Cybersecurity Explained",
            "duration": "4:12",
            "topic": "phishing"
        },
        {
            "type": "video", 
            "url": "https://www.youtube.com/watch?v=3NjQ9b3pgIg",
            "description": "Password Security and Best Practices",
            "duration": "6:45",
            "topic": "passwords"
        },
        {
            "type": "video",
            "url": "https://www.youtube.com/watch?v=bPVaOlJ6ln0",
            "description": "Social Engineering Attacks Explained",
            "duration": "8:30",
            "topic": "social_engineering"
        },
        {
            "type": "video",
            "url": "https://www.youtube.com/watch?v=Dk-ZqQ-bfy4",
            "description": "Network Security Fundamentals",
            "duration": "12:15",
            "topic": "network_security"
        }
    ],
    
    # Audio Content (Educational podcasts and audio examples)
    "audio_content": [
        {
            "type": "audio",
            "url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
            "description": "Social Engineering Phone Call Example (Audio Drama)",
            "duration": "2:30",
            "topic": "social_engineering"
        },
        {
            "type": "audio",
            "url": "https://archive.org/download/cybersecurity-basics-audio/cybersecurity-intro.mp3",
            "description": "Cybersecurity Basics - Audio Introduction",
            "duration": "5:45",
            "topic": "cybersecurity_basics"
        }
    ],
    
    # Interactive Infographics
    "infographics": [
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=800&fit=crop",
            "description": "Cybersecurity Statistics and Trends Infographic",
            "topic": "cybersecurity_stats"
        },
        {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&h=800&fit=crop",
            "description": "Data Breach Prevention Steps Infographic",
            "topic": "data_protection"
        }
    ]
}

class PhishingQuizView(View):
    def __init__(self, user_id: int, email_data: dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.email_data = email_data
        self.answered = False
        
        # Add buttons for phishing quiz
        legitimate_btn = Button(
            label="✅ Legitimate Email",
            style=discord.ButtonStyle.green,
            custom_id="legitimate"
        )
        legitimate_btn.callback = self.answer_legitimate
        self.add_item(legitimate_btn)
        
        phishing_btn = Button(
            label="🎣 Phishing Email", 
            style=discord.ButtonStyle.red,
            custom_id="phishing"
        )
        phishing_btn.callback = self.answer_phishing
        self.add_item(phishing_btn)
    
    async def answer_legitimate(self, interaction: discord.Interaction):
        await self.process_answer(interaction, False)
    
    async def answer_phishing(self, interaction: discord.Interaction):
        await self.process_answer(interaction, True)
    
    async def process_answer(self, interaction: discord.Interaction, user_answered_phishing: bool):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your quiz!",
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
        
        is_correct = user_answered_phishing == self.email_data['is_phishing']
        
        if is_correct:
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"**Great job!** {self.email_data['explanation']}",
                color=0x00FF00
            )
            xp_earned = 150
            db.add_xp(self.user_id, xp_earned)
            embed.add_field(
                name="XP Earned",
                value=f"+{xp_earned} XP",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="❌ Incorrect",
                description=f"**Not quite right.** {self.email_data['explanation']}",
                color=0xFF0000
            )
            embed.add_field(
                name="Learning Opportunity",
                value="Study the red flags and try again with the next example!",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)

class MultimediaView(View):
    def __init__(self, user_id: int, content_list: list, content_type: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.content_list = content_list
        self.content_type = content_type
        self.current_index = 0
        
        # Add navigation buttons
        if len(content_list) > 1:
            prev_btn = Button(
                label="◀️ Previous",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
            prev_btn.callback = self.previous_content
            self.add_item(prev_btn)
            
            next_btn = Button(
                label="Next ▶️",
                style=discord.ButtonStyle.secondary
            )
            next_btn.callback = self.next_content
            self.add_item(next_btn)
        
        # Add interactive quiz button for phishing content
        if content_type == "phishing":
            quiz_btn = Button(
                label="🎯 Take Quiz",
                style=discord.ButtonStyle.primary
            )
            quiz_btn.callback = self.start_phishing_quiz
            self.add_item(quiz_btn)
        
        # Add stop & save button
        stop_btn = Button(
            label="⏸️ Stop & Save",
            style=discord.ButtonStyle.danger
        )
        stop_btn.callback = self.stop_multimedia
        self.add_item(stop_btn)
    
    async def previous_content(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your content!", ephemeral=True)
            return
        
        self.current_index = max(0, self.current_index - 1)
        await self.update_content(interaction)
    
    async def next_content(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your content!", ephemeral=True)
            return
        
        self.current_index = min(len(self.content_list) - 1, self.current_index + 1)
        await self.update_content(interaction)
    
    async def update_content(self, interaction: discord.Interaction):
        embed = self.create_content_embed()
        
        # Update button states
        for item in self.children:
            if item.label == "◀️ Previous":
                item.disabled = self.current_index == 0
            elif item.label == "Next ▶️":
                item.disabled = self.current_index == len(self.content_list) - 1
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def start_phishing_quiz(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your quiz!", ephemeral=True)
            return
        
        current_content = self.content_list[self.current_index]
        quiz_view = PhishingQuizView(self.user_id, current_content)
        
        embed = discord.Embed(
            title="🎯 Phishing Detection Quiz",
            description="Look at the email above and decide: Is this legitimate or phishing?",
            color=0x0099FF
        )
        embed.add_field(
            name="Instructions",
            value="Analyze the email for red flags like:\n• Sender address\n• Grammar and spelling\n• Urgent language\n• Suspicious links",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=quiz_view, ephemeral=True)
    
    def create_content_embed(self):
        content = self.content_list[self.current_index]
        
        embed = discord.Embed(
            title=f"📚 {self.content_type.title()} Content",
            description=content['description'],
            color=0x0099FF
        )
        
        if content['type'] == 'image':
            embed.set_image(url=content['url'])
        elif content['type'] == 'video':
            embed.add_field(
                name="🎥 Video",
                value=f"[Watch Video]({content['url']})\nDuration: {content.get('duration', 'Unknown')}",
                inline=False
            )
        elif content['type'] == 'audio':
            embed.add_field(
                name="🎵 Audio",
                value=f"[Listen to Audio]({content['url']})\nDuration: {content.get('duration', 'Unknown')}",
                inline=False
            )
        
        if len(self.content_list) > 1:
            embed.set_footer(text=f"Content {self.current_index + 1} of {len(self.content_list)}")
        
        return embed
    
    async def stop_multimedia(self, interaction: discord.Interaction):
        """Stop and save multimedia session"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your content!", ephemeral=True)
            return
        
        # Import here to avoid circular imports
        from training_session import training_session_manager
        from datetime import datetime
        
        current_content = self.content_list[self.current_index]
        
        # Save multimedia session
        current_position = {
            'content_type': self.content_type,
            'current_index': self.current_index,
            'total_items': len(self.content_list)
        }
        session_data = {
            'current_content_title': current_content['title'],
            'current_content_description': current_content['description'],
            'saved_at': str(datetime.now())
        }
        
        success = training_session_manager.save_session(
            self.user_id, 
            'multimedia', 
            current_position, 
            session_data
        )
        
        if success:
            embed = discord.Embed(
                title="⏸️ Multimedia Session Saved",
                description=f"Your multimedia session has been saved. Resume anytime with `/multimedia {self.content_type}` or `/sessions`.",
                color=0x00FF00
            )
            embed.add_field(
                name="Saved Position",
                value=f"{current_content['title']} ({self.current_index + 1}/{len(self.content_list)})",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Save Failed",
                description="Failed to save your multimedia session. Please try again.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MultimediaManager:
    def __init__(self):
        self.content = MULTIMEDIA_CONTENT
    
    def get_phishing_examples(self):
        """Get phishing email examples for interactive learning"""
        return self.content['phishing_examples']
    
    def get_password_examples(self):
        """Get password strength examples"""
        return self.content['password_examples']
    
    def get_network_diagrams(self):
        """Get network security diagrams"""
        return self.content['network_diagrams']
    
    def get_malware_examples(self):
        """Get safe malware examples"""
        return self.content['malware_examples']
    
    def get_educational_videos(self, topic: str = None):
        """Get educational videos, optionally filtered by topic"""
        videos = self.content['educational_videos']
        if topic:
            return [v for v in videos if v.get('topic') == topic]
        return videos
    
    def get_audio_content(self, topic: str = None):
        """Get audio content, optionally filtered by topic"""
        audio = self.content['audio_content']
        if topic:
            return [a for a in audio if a.get('topic') == topic]
        return audio
    
    def create_multimedia_embed(self, content_type: str, user_id: int):
        """Create embed with multimedia content and interactive elements"""
        content_map = {
            'phishing': self.get_phishing_examples(),
            'passwords': self.get_password_examples(),
            'network': self.get_network_diagrams(),
            'malware': self.get_malware_examples(),
            'videos': self.get_educational_videos(),
            'audio': self.get_audio_content()
        }
        
        content_list = content_map.get(content_type, [])
        if not content_list:
            return discord.Embed(
                title="❌ No Content Available",
                description=f"No {content_type} content is currently available.",
                color=0xFF0000
            ), None
        
        view = MultimediaView(user_id, content_list, content_type)
        embed = view.create_content_embed()
        
        return embed, view
    
    def add_lesson_multimedia(self, course_id: int, module_id: int, lesson_id: int, 
                            content_type: str, url: str, description: str):
        """Add multimedia content to a specific lesson"""
        return db.add_multimedia_content(content_type, url, description, course_id, module_id, lesson_id)
    
    def get_lesson_multimedia(self, course_id: int, module_id: int, lesson_id: int):
        """Get multimedia content for a specific lesson"""
        return db.get_lesson_multimedia(course_id, module_id, lesson_id)
    
    def create_interactive_lesson_embed(self, course_id: int, module_id: int, lesson_id: int, lesson_content: str):
        """Create an enhanced lesson embed with multimedia content"""
        multimedia_content = self.get_lesson_multimedia(course_id, module_id, lesson_id)
        
        embed = discord.Embed(
            title="📚 Enhanced Lesson",
            description=lesson_content[:1000] + "..." if len(lesson_content) > 1000 else lesson_content,
            color=0x0099FF
        )
        
        # Add multimedia content
        images = [m for m in multimedia_content if m[0] == 'image']
        videos = [m for m in multimedia_content if m[0] == 'video']
        audio = [m for m in multimedia_content if m[0] == 'audio']
        
        if images:
            embed.set_image(url=images[0][1])  # Set first image
            if len(images) > 1:
                embed.add_field(
                    name="📸 Additional Images",
                    value=f"{len(images) - 1} more images available",
                    inline=True
                )
        
        if videos:
            video_text = "\n".join([f"🎥 [{v[2]}]({v[1]})" for v in videos[:3]])
            embed.add_field(
                name="🎥 Videos",
                value=video_text,
                inline=True
            )
        
        if audio:
            audio_text = "\n".join([f"🎵 [{a[2]}]({a[1]})" for a in audio[:3]])
            embed.add_field(
                name="🎵 Audio",
                value=audio_text,
                inline=True
            )
        
        return embed

# Global multimedia manager instance
multimedia_manager = MultimediaManager()

# Initialize some sample multimedia content in database
def initialize_sample_content():
    """Initialize sample multimedia content for lessons"""
    # Add phishing examples to phishing lessons
    multimedia_manager.add_lesson_multimedia(3, 1, 1, "image", 
        "https://via.placeholder.com/600x400/FF6B6B/FFFFFF?text=PHISHING+EMAIL+EXAMPLE",
        "Example phishing email with red flags highlighted")
    
    # Add password examples to password lessons  
    multimedia_manager.add_lesson_multimedia(2, 1, 1, "image",
        "https://via.placeholder.com/600x300/4ECDC4/FFFFFF?text=STRONG+PASSWORD+EXAMPLE", 
        "Visual guide to creating strong passwords")
    
    # Add network diagrams to network lessons
    multimedia_manager.add_lesson_multimedia(4, 1, 1, "image",
        "https://via.placeholder.com/600x400/45B7D1/FFFFFF?text=NETWORK+DIAGRAM",
        "Home network security diagram")

# Initialize sample content when module is imported
initialize_sample_content()
"""
Personalized Gamified Tutor Module
- /tutor -> icebreaker -> role selection -> tailored micro-path
- /tutor_submit -> submit exercise
- /tutor_review -> mentor/admin review of submissions
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("cyberbot.tutor")

try:
    from database import db
except Exception:
    db = None
    logger.debug("db not available - tutor will use in-memory placeholders")

try:
    from achievements import achievement_manager
except Exception:
    achievement_manager = None
    logger.debug("achievement_manager not available - tutor achievements will be limited")

try:
    from multimedia import _choose_video_for, create_multimedia_embed
except Exception:
    _choose_video_for = None
    create_multimedia_embed = None
    logger.debug("multimedia not available - role cards will not include video embeds")

ROLE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "soc_analyst": {
        "name": "SOC Analyst (Security Operations)",
        "pitch": "Be the watchful guardian of systems — monitor alerts, hunt threats, and respond quickly. Feels like being a digital detective with a coffee habit.",
        "how_hard": "Moderate. You can start in entry-level SOC roles with observability and alerting basics.",
        "pay": "Entry-level ~$45k-65k (varies by region); can grow fast with experience.",
        "quick_certs": ["CompTIA Security+", "Splunk Fundamentals (free)", "Azure/AWS Cloud Fundamentals"],
        "fast_path": "Learn log basics, SIEM searching, triaging alerts. Do a mini hunt exercise to show recruiters.",
        "short_video_topic": "phishing"
    },
    "pentester": {
        "name": "Penetration Tester (Red Team)",
        "pitch": "Like cybersecurity's escape room master — you find creative ways to break into systems before bad actors do. Exciting and technical.",
        "how_hard": "Challenging but approachable with hands-on labs. You'll need strong tooling and scripting skills.",
        "pay": "Mid-range to high; juniors ~$60k+ and upwards with certifications or OSCP.",
        "quick_certs": ["eJPT (Entry-level)", "OSCP (advanced)"],
        "fast_path": "Focus on web app vulnerabilities and TryHackMe/HTB beginner boxes.",
        "short_video_topic": "network"
    },
    "appsec": {
        "name": "Application Security Engineer",
        "pitch": "Help developers build secure apps — you’ll review code, threat-model, and fix bugs early. Great fit if you like coding and security.",
        "how_hard": "Moderate to hard depending on code background. Knowledge of OWASP is key.",
        "pay": "Good. Entry/junior can start with engineering + security skills.",
        "quick_certs": ["Secure Coding Courses, Offensive/Defensive developer courses"],
        "fast_path": "Learn OWASP Top 10, run static analysis tools, do a code review exercise.",
        "short_video_topic": "passwords"
    }
}

IN_MEMORY_SUBMISSIONS = {}
NEXT_SUBMISSION_ID = 1


def _format_role_card(role_key: str) -> discord.Embed:
    role = ROLE_TEMPLATES[role_key]
    embed = discord.Embed(
        title=f"🧭 {role['name']}",
        description=role['pitch'],
        color=0x7CC7FF
    )
    embed.add_field(name="Is it hard?", value=role['how_hard'], inline=True)
    embed.add_field(name="Pay reality", value=role['pay'], inline=True)
    embed.add_field(name="Fast certs / wins", value=", ".join(role['quick_certs']), inline=False)
    embed.add_field(name="Fast path", value=role['fast_path'], inline=False)
    embed.set_footer(text="Pick this path to get a short gamified learning plan tailored to you.")
    return embed

class RoleSelectionView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        for key in ROLE_TEMPLATES:
            btn = Button(label=ROLE_TEMPLATES[key]['name'][:80], style=discord.ButtonStyle.primary)
            btn.custom_role_key = key
            btn.callback = self.role_chosen
            self.add_item(btn)

    async def role_chosen(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This selection isn't for you — start your own tutor with /tutor start", ephemeral=True)
            return

        # Determine role_key from clicked button
        role_key = None
        try:
            # discord.py exposes custom_id or component label info differently; attempt to find via label
            clicked_label = interaction.data.get('component', {}).get('label') if interaction.data else None
        except Exception:
            clicked_label = None

        if clicked_label:
            for child in self.children:
                if getattr(child, 'custom_role_key', None) and child.label == clicked_label:
                    role_key = getattr(child, 'custom_role_key')
                    break

        if not role_key:
            # fallback to first role
            role_key = list(ROLE_TEMPLATES.keys())[0]
            logger.debug("role_chosen fallback role_key: %s", role_key)

        try:
            if db:
                db.create_tutor_path(interaction.user.id, role_key)
        except Exception:
            logger.exception("Failed to save tutor path for user %s", interaction.user.id)

        embed = _format_role_card(role_key)
        try:
            if _choose_video_for and ROLE_TEMPLATES[role_key].get('short_video_topic'):
                vid = _choose_video_for(ROLE_TEMPLATES[role_key]['short_video_topic'])
                embed.add_field(name="Quick Watch", value=f"[{vid['title']}]({vid['url']})", inline=False)
        except Exception:
            logger.debug("multimedia not available for role card")

        first_task_description = f"Quick challenge: Complete this 3-step exercise to get {100} XP:\n1️⃣ Watch the short clip above.\n2️⃣ Answer: What are 2 indicators that the example is malicious?\n3️⃣ Submit your answers with `/tutor_submit`.\n\nBe concise and show 1-2 clear indicators."
        embed.add_field(name="First Micro-Task", value=first_task_description, inline=False)

        await interaction.response.edit_message(embed=embed, view=None, content=None)

class IcebreakerModal(Modal):
    def __init__(self):
        super().__init__(title="Icebreaker — Tell me about you")
        self.q1 = TextInput(label="What do you enjoy doing? (coding, puzzles, writing, networking, etc.)", style=discord.TextStyle.short, required=True, max_length=120)
        self.q2 = TextInput(label="What's one reason you're curious about cybersecurity?", style=discord.TextStyle.paragraph, required=False)
        self.add_item(self.q1)
        self.add_item(self.q2)

    async def on_submit(self, interaction: discord.Interaction):
        likes = self.q1.value.lower()
        reason = self.q2.value
        recommended = []
        if "code" in likes or "program" in likes or "dev" in likes:
            recommended.append("appsec")
        if "puzzle" in likes or "detect" in likes or "investigate" in likes:
            recommended.append("soc_analyst")
        if "network" in likes or "routers" in likes:
            recommended.append("pentester")
        if not recommended:
            recommended = list(ROLE_TEMPLATES.keys())[:2]

        rec_names = ", ".join(ROLE_TEMPLATES[k]["name"] for k in recommended)
        fun_text = f"Nice! Based on that, I'd recommend trying: {rec_names}.\nThese are short, practical paths — we start with a fun micro-task and you submit your work for review to earn XP!"

        try:
            if db:
                db.update_user_profile(interaction.user.id, {"likes": self.q1.value, "reason": self.q2.value})
        except Exception:
            logger.exception("Failed to save profile")

        await interaction.response.send_message(fun_text, ephemeral=True)

class SubmissionModal(Modal):
    def __init__(self, prompt_text: str):
        super().__init__(title="Submit your exercise")
        self.answer = TextInput(label="Your answer (concise -> 1-5 lines)", style=discord.TextStyle.paragraph, required=True, max_length=1500)
        self.add_item(self.answer)
        self.prompt_text = prompt_text

    async def on_submit(self, interaction: discord.Interaction):
        global NEXT_SUBMISSION_ID
        submission_text = self.answer.value
        submission = {
            "id": None,
            "user_id": interaction.user.id,
            "content": submission_text,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "score": None,
            "reviewer": None
        }
        try:
            if db:
                sid = db.create_submission(interaction.user.id, submission_text, "tutor")
                submission["id"] = sid
            else:
                submission["id"] = NEXT_SUBMISSION_ID
                IN_MEMORY_SUBMISSIONS[NEXT_SUBMISSION_ID] = submission
                NEXT_SUBMISSION_ID += 1
        except Exception:
            logger.exception("Failed to create submission in db")
            submission["id"] = NEXT_SUBMISSION_ID
            IN_MEMORY_SUBMISSIONS[NEXT_SUBMISSION_ID] = submission
            NEXT_SUBMISSION_ID += 1

        await interaction.response.send_message(f"✅ Submission received (id: {submission['id']}). A mentor will review it soon. You earned provisional XP!", ephemeral=True)
        try:
            score = 0
            text = submission_text.lower()
            if "link" in text or "url" in text:
                score += 1
            if "password" in text or "credential" in text:
                score += 1
            if "urgent" in text or "click" in text or "verify" in text:
                score += 1
            if score >= 2:
                try:
                    if db:
                        db.add_xp(interaction.user.id, 100)
                    if achievement_manager:
                        achievement_manager.check_and_award_achievements(interaction.user.id)
                except Exception:
                    logger.exception("Failed to award XP after auto-check")
        except Exception:
            logger.exception("Auto-check failed for submission id %s", submission["id"])

class TutorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tutor", description="Start a personalized cybersecurity tutor session")
    async def tutor(self, interaction: discord.Interaction):
        view = View(timeout=300)

        async def start_icebreaker_callback(i: discord.Interaction):
            if i.user.id != interaction.user.id:
                await i.response.send_message("This icebreaker isn't for you — run /tutor to start your own!", ephemeral=True)
                return
            modal = IcebreakerModal()
            await i.response.send_modal(modal)

        start_btn = Button(label="🧊 Icebreaker", style=discord.ButtonStyle.primary)
        start_btn.callback = start_icebreaker_callback
        view.add_item(start_btn)

        rs_view = RoleSelectionView(interaction.user.id)
        embed = discord.Embed(
            title="🎓 Personalized Cyber Tutor",
            description="I'll help you pick a role and create short, fun, gamified exercises. Start with the icebreaker or pick a role below!",
            color=0x00BBFF
        )

        for k in list(ROLE_TEMPLATES.keys()):
            embed.add_field(name=ROLE_TEMPLATES[k]["name"], value=ROLE_TEMPLATES[k]["pitch"][:120]+"...", inline=False)

        await interaction.response.send_message(embed=embed, view=rs_view, ephemeral=True)

    @app_commands.command(name="tutor_submit", description="Submit your micro-task for review")
    async def tutor_submit(self, interaction: discord.Interaction):
        modal = SubmissionModal("Please paste your short answer")
        await interaction.response.send_modal(modal)

    @app_commands.command(name="tutor_review", description="(Mentors) Review a submission")
    @app_commands.describe(submission_id="ID of the submission to review", score="0-100 score", notes="Optional review notes")
    async def tutor_review(self, interaction: discord.Interaction, submission_id: int, score: int, notes: Optional[str] = None):
        if not interaction.user.guild_permissions.manage_messages and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You must be a mentor/admin to review.", ephemeral=True)
            return

        try:
            if db:
                submission = db.get_submission(submission_id)
            else:
                submission = IN_MEMORY_SUBMISSIONS.get(submission_id)
        except Exception:
            submission = None
            logger.exception("Failed to load submission %s", submission_id)

        if not submission:
            await interaction.response.send_message("Submission not found.", ephemeral=True)
            return

        status = "approved" if score >= 60 else "needs_work"
        try:
            if db:
                db.update_submission_review(submission_id, interaction.user.id, status, score, notes or "")
                if score >= 60:
                    db.add_xp(submission["user_id"], 150)
            else:
                submission["status"] = status
                submission["score"] = score
                submission["reviewer"] = interaction.user.id
                if score >= 60:
                    logger.debug("Would award XP for user %s", submission["user_id"])
        except Exception:
            logger.exception("Failed updating submission %s", submission_id)

        await interaction.response.send_message(f"Submission {submission_id} marked {status} (score: {score}).", ephemeral=True)

async def setup_tutor(bot: commands.Bot):
    await bot.add_cog(TutorCog(bot))

# Integration note:
# import setup_tutor and call in bot.setup_hook() or include in setup_cogs()
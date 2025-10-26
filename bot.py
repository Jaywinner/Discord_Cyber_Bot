"""
Enhanced Cybersecurity Learning Discord Bot
Interactive, gamified cybersecurity education platform
"""

import logging
import os
import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyberbot")

# Import our custom modules
from database import db
from courses import get_course, get_lesson, get_next_lesson, get_course_list, get_module
from achievements import achievement_manager
from quiz import quiz_manager
from admin import AdminCommands
from ctf import ctf_manager, CTFChallengeView
# multimedia manager may be provided; we also now have multimedia.py
from multimedia import create_multimedia_embed, _choose_video_for
from multimedia import multimedia_manager if 'multimedia_manager' in globals() else None
from training_session import training_session_manager, StopResumeView
from tutor import setup_tutor

# Bot configuration (from environment to avoid hardcoded values)
PREFIX = os.getenv("BOT_PREFIX", "!")
GUILD_ID = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


async def setup_cogs():
    await bot.add_cog(AdminCommands(bot))
    # setup tutor cog
    try:
        await setup_tutor(bot)
    except Exception:
        logger.exception("Failed to setup tutor cog")


@bot.event
async def setup_hook():
    await setup_cogs()

# (rest of bot.py remains unchanged and is assumed to be present in the branch)
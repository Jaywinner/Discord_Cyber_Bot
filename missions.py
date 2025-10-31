"""
Story-driven Missions System
Implements interactive, narrative scenarios aligned with learning outcomes.
"""

import discord
from discord.ui import Button, View
import json
from typing import Dict, Any, List, Optional
from database import db


class MissionView(View):
    def __init__(self, user_id: int, mission_code: str, step_index: int, step: Dict[str, Any]):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.mission_code = mission_code
        self.step_index = step_index
        self.step = step

        options: List[Dict[str, Any]] = json.loads(step.get("options_json", "[]"))
        for i, opt in enumerate(options[:4]):
            btn = Button(
                label=opt.get("label", f"Option {i+1}"),
                style=discord.ButtonStyle.primary if opt.get("correct") else discord.ButtonStyle.secondary,
                custom_id=f"mission_opt_{i}"
            )
            btn.callback = self._make_option_callback(opt)
            self.add_item(btn)

        stop_btn = Button(label="⏸️ Stop & Save", style=discord.ButtonStyle.secondary)
        stop_btn.callback = self._save_session
        self.add_item(stop_btn)

    def _make_option_callback(self, option: Dict[str, Any]):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This isn't your mission!", ephemeral=True)
                return

            # Award XP if defined
            xp = int(option.get("xp", 0) or 0)
            if xp > 0:
                db.add_xp(self.user_id, xp)

            # Update mission progress
            next_step = option.get("next_step")
            status = "completed" if next_step is None else "in_progress"
            self._update_progress(self.user_id, self.mission_code, next_step if next_step is not None else self.step_index)

            # Build feedback embed with consequence text
            embed = discord.Embed(
                title="📖 Consequence",
                description=option.get("consequence", ""),
                color=0x00FF00 if option.get("correct") else 0xFF8000
            )

            if next_step is None:
                embed.title = "🎉 Mission Complete"
                embed.add_field(name="Status", value="Completed", inline=True)
                await interaction.response.edit_message(embed=embed, view=None)
                return

            # Load next step
            step = get_mission_step(self.mission_code, next_step)
            next_embed, next_view = create_mission_step_embed(self.user_id, self.mission_code, next_step, step)
            await interaction.response.edit_message(embed=next_embed, view=next_view)

        return callback

    async def _save_session(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your mission!", ephemeral=True)
            return
        from training_session import training_session_manager
        current_position = {
            'mission_code': self.mission_code,
            'step_index': self.step_index
        }
        session_data = {
            'prompt': self.step.get('prompt')
        }
        training_session_manager.save_session(self.user_id, 'mission', current_position, session_data)
        embed = discord.Embed(
            title="⏸️ Mission Saved",
            description="Resume anytime with /mission resume",
            color=0x0099FF
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def _update_progress(self, user_id: int, mission_code: str, step_index: Optional[int]):
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            if step_index is None:
                cursor.execute(
                    """
                    INSERT INTO mission_progress (user_id, mission_code, current_step, status)
                    VALUES (?, ?, 0, 'completed')
                    ON CONFLICT DO NOTHING
                    """,
                    (user_id, mission_code)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO mission_progress (user_id, mission_code, current_step, status)
                    VALUES (?, ?, ?, 'in_progress')
                """,
                    (user_id, mission_code, step_index)
                )
        except Exception:
            pass
        finally:
            try:
                conn.commit()
            except Exception:
                pass
            conn.close()


def ensure_sample_mission():
    """Seed a simple phishing narrative mission if not present."""
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM missions WHERE code = ?", ("phish_alice_1",))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO missions (code, title, narrative, learning_outcomes, min_xp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "phish_alice_1",
                    "Alice and the Suspicious Invoice",
                    "Alice receives a surprising invoice email late on Friday.",
                    "Recognize red flags; verify sender; avoid clicking links.",
                    0,
                ),
            )
            steps = [
                (
                    0,
                    "You see an email: 'Overdue invoice attached'. What do you do?",
                    [
                        {"label": "Open the attachment", "next_step": 1, "correct": False, "consequence": "Malware was executed. Systems at risk.", "xp": 0},
                        {"label": "Verify sender and domain", "next_step": 2, "correct": True, "consequence": "Good call. The domain looks off.", "xp": 100},
                    ],
                ),
                (
                    1,
                    "Your AV alerts on the file. What's next?",
                    [
                        {"label": "Report to IT/security channel", "next_step": 3, "correct": True, "consequence": "Incident contained quickly.", "xp": 150},
                        {"label": "Ignore and move on", "next_step": 3, "correct": False, "consequence": "Potential spread increases.", "xp": 0},
                    ],
                ),
                (
                    2,
                    "The sender's domain uses a homoglyph. Next action?",
                    [
                        {"label": "Hover link and inspect URL", "next_step": 3, "correct": True, "consequence": "Link goes to shady-shortener.biz.", "xp": 150},
                        {"label": "Forward to colleagues", "next_step": 3, "correct": False, "consequence": "Risk propagates.", "xp": 0},
                    ],
                ),
                (
                    3,
                    "Wrap up",
                    [
                        {"label": "Report phishing and delete", "next_step": None, "correct": True, "consequence": "Mission success. Alice stays safe.", "xp": 200},
                    ],
                ),
            ]
            for step_index, prompt, options in steps:
                cursor.execute(
                    """
                    INSERT INTO mission_steps (mission_code, step_index, prompt, options_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("phish_alice_1", step_index, prompt, json.dumps(options)),
                )
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()


def get_mission_step(mission_code: str, step_index: int) -> Dict[str, Any]:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT prompt, options_json FROM mission_steps WHERE mission_code = ? AND step_index = ?",
            (mission_code, step_index),
        )
        row = cursor.fetchone()
        if not row:
            return {}
        return {"prompt": row[0], "options_json": row[1]}
    finally:
        conn.close()


def create_mission_step_embed(user_id: int, mission_code: str, step_index: int, step: Dict[str, Any]):
    prompt = step.get("prompt", "")
    options = json.loads(step.get("options_json", "[]"))
    embed = discord.Embed(
        title=f"🕵️ Mission: {mission_code} — Step {step_index}",
        description=prompt,
        color=0x0099FF,
    )
    if options:
        opts_txt = "\n".join([f"• {opt.get('label')}" for opt in options])
        embed.add_field(name="Choices", value=opts_txt, inline=False)
    view = MissionView(user_id, mission_code, step_index, step)
    return embed, view


class MissionsManager:
    def __init__(self):
        ensure_sample_mission()

    def start_mission(self, user_id: int, mission_code: str):
        step = get_mission_step(mission_code, 0)
        return create_mission_step_embed(user_id, mission_code, 0, step)


missions_manager = MissionsManager()



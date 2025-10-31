"""
Micro-learning and Spaced Repetition
Provides daily/weekly tips and resurfacing weak topics.
"""

import random
import discord
from typing import Tuple
from database import db


TIPS = [
    ("phishing", "Pause before you click. Hover links to preview the real URL."),
    ("passwords", "Use passphrases: four random words beat complex single words."),
    ("2fa", "Enable 2FA wherever possible; prefer app-based codes over SMS."),
    ("updates", "Apply updates promptly. Most breaches exploit known, patched flaws."),
    ("wifi", "On public Wi‑Fi, avoid sensitive logins unless you're on a VPN."),
]


def pick_spaced_tip(user_id: int) -> Tuple[str, str, str]:
    """Select a tip prioritizing topics where the user underperforms or hasn't seen recently."""
    # Simple heuristic: if avg < 70, prioritize quiz topics from recent attempts; else random excluding last seen topics
    conn = db.get_connection()
    cursor = conn.cursor()
    weak_topics = []
    try:
        cursor.execute(
            """
            SELECT module_id, AVG(CAST(score AS FLOAT)/total_questions*100) as pct
            FROM quiz_attempts WHERE user_id = ? GROUP BY module_id HAVING pct < 70
            ORDER BY pct ASC LIMIT 3
            """,
            (user_id,),
        )
        weak_rows = cursor.fetchall() or []
        weak_map = {r[0]: r[1] for r in weak_rows}
        if weak_map:
            for module_id in weak_map.keys():
                # Map module IDs to generic topics
                topic = {
                    1: "phishing",
                    2: "passwords",
                    3: "2fa",
                    4: "wifi",
                }.get(module_id, "updates")
                weak_topics.append(topic)
    except Exception:
        pass
    finally:
        conn.close()

    recent = set(db.get_recent_topics_for_user(user_id, limit=3))
    candidates = [t for t in TIPS if t[0] not in recent]
    if weak_topics:
        candidates = [t for t in TIPS if t[0] in weak_topics and t[0] not in recent] or candidates

    topic, text = random.choice(candidates if candidates else TIPS)
    tip_id = f"{topic}:{abs(hash(text))%100000}"
    return topic, tip_id, text


async def send_daily_tip(ctx, user_id: int):
    topic, tip_id, text = pick_spaced_tip(user_id)
    embed = discord.Embed(
        title=f"💡 Daily Cyber Tip — {topic.title()}",
        description=text,
        color=0x00CC66,
    )
    embed.set_footer(text="React with ✅ if this was helpful")
    msg = await ctx.send(embed=embed)
    try:
        await msg.add_reaction("✅")
        await msg.add_reaction("❓")
    except Exception:
        pass
    db.log_tip_delivery(user_id, topic, tip_id)
    return msg



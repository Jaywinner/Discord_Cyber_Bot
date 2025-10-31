"""
Personalization and Adaptive Recommendations
Recommends next topics and difficulty based on history.
"""

from typing import Tuple
from database import db


def recommend_next(user_id: int) -> Tuple[int, int, int, str]:
    """
    Recommend (course_id, module_id, lesson_id, rationale) based on quiz performance and track.
    Simple heuristic:
    - If last_7_avg < 60: suggest easier module (module 1) in current course with remediation.
    - If 60-80: suggest continuing current path.
    - If >80: suggest advanced or CTF unlock preview.
    """
    stats = db.get_user_stats(user_id)
    if not stats:
        return 1, 1, 1, "New learner: starting fundamentals."
    _, _, _, course_id, module_id, lesson_id = stats

    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT last_7_avg FROM user_metrics WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        last7 = row[0] if row else 0
    except Exception:
        last7 = 0
    finally:
        conn.close()

    if last7 < 60:
        return course_id, 1, 1, "Focusing on foundations based on recent scores."
    if last7 < 80:
        return course_id, module_id, lesson_id, "Continue your current path for steady progress."
    return course_id, min(module_id + 1, module_id + 1), 1, "Great performance! Advancing difficulty."


def set_track(user_id: int, track: str):
    if track not in ("beginner", "student", "small_business"):
        track = "beginner"
    db.set_user_track(user_id, track)


def get_track(user_id: int) -> str:
    return db.get_user_track(user_id)



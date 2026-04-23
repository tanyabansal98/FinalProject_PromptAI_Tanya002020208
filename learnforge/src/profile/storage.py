"""SQLite storage for learning progress, quiz scores, and knowledge gaps."""
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from src.config import SQLITE_DB_PATH

logger = logging.getLogger(__name__)


def get_conn(db_path=None):
    conn = sqlite3.connect(str(db_path or SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    conn = get_conn(db_path)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                topic TEXT NOT NULL,
                level TEXT NOT NULL,
                curriculum_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                session_id INTEGER,
                module_id TEXT,
                topic TEXT,
                question_id TEXT,
                question_text TEXT,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct INTEGER,
                score INTEGER DEFAULT 0,
                bloom_level TEXT,
                gap_tags TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS knowledge_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                tag TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                topic TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, tag, topic)
            );
            CREATE TABLE IF NOT EXISTS flashcard_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                card_id TEXT,
                module_id TEXT,
                confidence INTEGER DEFAULT 0,
                times_seen INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0,
                next_review TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, card_id)
            );
            CREATE TABLE IF NOT EXISTS study_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                date TEXT NOT NULL,
                minutes_studied INTEGER DEFAULT 0,
                modules_completed INTEGER DEFAULT 0,
                quizzes_taken INTEGER DEFAULT 0,
                UNIQUE(user_id, date)
            );
        """)
        conn.commit()
    finally:
        conn.close()


def save_quiz_result(user_id, session_id, module_id, topic, question_id, question_text,
                     user_answer, correct_answer, is_correct, score, bloom_level, gap_tags, feedback, db_path=None):
    conn = get_conn(db_path)
    try:
        conn.execute(
            """INSERT INTO quiz_results (user_id, session_id, module_id, topic, question_id,
               question_text, user_answer, correct_answer, is_correct, score, bloom_level, gap_tags, feedback)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, session_id, module_id, topic, question_id, question_text,
             user_answer, correct_answer, int(is_correct), score, bloom_level,
             json.dumps(gap_tags), feedback))
        conn.commit()
    finally:
        conn.close()


def update_knowledge_gaps(user_id, gap_tags, topic, db_path=None):
    conn = get_conn(db_path)
    try:
        for tag in gap_tags:
            conn.execute(
                """INSERT INTO knowledge_gaps (user_id, tag, count, topic, last_seen)
                   VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(user_id, tag, topic) DO UPDATE SET
                   count = count + 1, last_seen = CURRENT_TIMESTAMP""",
                (user_id, tag, topic))
        conn.commit()
    finally:
        conn.close()


def get_quiz_history(user_id, limit=100, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM quiz_results WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_knowledge_gaps(user_id, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT tag, count, topic, last_seen FROM knowledge_gaps WHERE user_id = ? ORDER BY count DESC",
            (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_topic_scores(user_id, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            """SELECT topic, module_id, bloom_level,
                      AVG(score) as avg_score, COUNT(*) as total,
                      SUM(is_correct) as correct_count
               FROM quiz_results WHERE user_id = ?
               GROUP BY topic, module_id""",
            (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_bloom_distribution(user_id, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            """SELECT bloom_level, COUNT(*) as total, SUM(is_correct) as correct,
                      AVG(score) as avg_score
               FROM quiz_results WHERE user_id = ?
               GROUP BY bloom_level""",
            (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_daily_activity(user_id, days=30, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            """SELECT DATE(created_at) as date, COUNT(*) as questions_answered,
                      SUM(is_correct) as correct, AVG(score) as avg_score
               FROM quiz_results WHERE user_id = ?
               GROUP BY DATE(created_at) ORDER BY date DESC LIMIT ?""",
            (user_id, days)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_flashcard_progress(user_id, card_id, module_id, correct, db_path=None):
    conn = get_conn(db_path)
    try:
        conn.execute(
            """INSERT INTO flashcard_progress (user_id, card_id, module_id, confidence, times_seen, times_correct)
               VALUES (?, ?, ?, ?, 1, ?)
               ON CONFLICT(user_id, card_id) DO UPDATE SET
               confidence = CASE WHEN ? THEN MIN(confidence + 1, 5) ELSE MAX(confidence - 1, 0) END,
               times_seen = times_seen + 1,
               times_correct = times_correct + ?,
               updated_at = CURRENT_TIMESTAMP""",
            (user_id, card_id, module_id, 1 if correct else 0, int(correct),
             correct, int(correct)))
        conn.commit()
    finally:
        conn.close()


def log_study_activity(user_id, minutes=0, modules=0, quizzes=0, db_path=None):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn(db_path)
    try:
        conn.execute(
            """INSERT INTO study_streaks (user_id, date, minutes_studied, modules_completed, quizzes_taken)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(user_id, date) DO UPDATE SET
               minutes_studied = minutes_studied + ?,
               modules_completed = modules_completed + ?,
               quizzes_taken = quizzes_taken + ?""",
            (user_id, today, minutes, modules, quizzes, minutes, modules, quizzes))
        conn.commit()
    finally:
        conn.close()


def get_streak(user_id, db_path=None):
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT date FROM study_streaks WHERE user_id = ? ORDER BY date DESC LIMIT 30",
            (user_id,)).fetchall()
        return [r["date"] for r in rows]
    finally:
        conn.close()

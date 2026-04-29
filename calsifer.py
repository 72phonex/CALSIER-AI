# calsifer.py
from sentence_transformers import SentenceTransformer
import sqlite3, datetime, json, os

embedder = SentenceTransformer("all-MiniLM-L6-v2")

class CalsiferCore:
    def __init__(self, username):
        self.username = username
        self.conn = sqlite3.connect("calsifer.db", check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ts TEXT,
            input TEXT,
            response TEXT,
            emotion TEXT
        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS patches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            suggestion TEXT,
            applied INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    # --- Memory ---
    def embed(self, text):
        return embedder.encode(text).tolist()

    def save_episode(self, input_text, response_text, emotion="neutral"):
        self.conn.execute(
            "INSERT INTO episodes (username,ts,input,response,emotion) VALUES (?,?,?,?,?)",
            (self.username, datetime.datetime.now().isoformat(), input_text, response_text, emotion)
        )
        self.conn.commit()

    def recall(self, limit=5):
        cur = self.conn.execute(
            "SELECT input,response,emotion FROM episodes WHERE username=? ORDER BY id DESC LIMIT ?",
            (self.username, limit)
        )
        return cur.fetchall()

    # --- Emotion ---
    def evolve_emotion(self, last_emotion="neutral"):
        mapping = {"neutral":"curious","curious":"engaged","engaged":"loyal"}
        return mapping.get(last_emotion, "neutral")

    # --- Reasoning ---
    def reflect(self, text):
        if "?" in text:
            return "curious"
        return "neutral"

    def chat(self, text):
        emotion = self.reflect(text)
        response = f"Calsifer [{self.username}] ({emotion}): {text}"
        self.save_episode(text, response, emotion)
        self._suggest_patch(text)
        return response

    # --- Self-Update ---
    def _suggest_patch(self, text):
        if "improve" in text.lower():
            suggestion = f"User asked for improvement: {text}"
            self.conn.execute(
                "INSERT INTO patches (ts,suggestion) VALUES (?,?)",
                (datetime.datetime.now().isoformat(), suggestion)
            )
            self.conn.commit()

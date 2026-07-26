"""
Chat history management using SQLite.
Handles multiple chats per browser session: create, list, rename, delete, search.
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "chat_history.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    """)

    conn.commit()
    conn.close()


def create_chat(session_id: str, title: str = "New Chat") -> str:
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (id, session_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (chat_id, session_id, title, now, now)
    )
    conn.commit()
    conn.close()

    return chat_id


def get_chats(session_id: str) -> list:
    """Returns chats for this session, most recently updated first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, updated_at FROM chats WHERE session_id = ? ORDER BY updated_at DESC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_messages(chat_id: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, source FROM messages WHERE chat_id = ? ORDER BY id ASC",
        (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_message(chat_id: str, role: str, content: str, source: str = None):
    now = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, role, content, source, created_at) VALUES (?, ?, ?, ?, ?)",
        (chat_id, role, content, source, now)
    )

    # Update chat's updated_at timestamp (for sorting by recency)
    cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))

    # Auto-generate title from first user message if still default
    cursor.execute("SELECT title FROM chats WHERE id = ?", (chat_id,))
    current_title = cursor.fetchone()["title"]
    if current_title == "New Chat" and role == "user":
        new_title = content[:40] + ("..." if len(content) > 40 else "")
        cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))

    conn.commit()
    conn.close()


def rename_chat(chat_id: str, new_title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))
    conn.commit()
    conn.close()


def delete_chat(chat_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


def search_chats(session_id: str, query: str) -> list:
    """Search chats by title OR message content."""
    conn = get_connection()
    cursor = conn.cursor()
    like_query = f"%{query}%"
    cursor.execute("""
        SELECT DISTINCT c.id, c.title, c.updated_at
        FROM chats c
        LEFT JOIN messages m ON c.id = m.chat_id
        WHERE c.session_id = ? AND (c.title LIKE ? OR m.content LIKE ?)
        ORDER BY c.updated_at DESC
    """, (session_id, like_query, like_query))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
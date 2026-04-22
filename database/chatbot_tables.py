import os, sqlite3

from config import SQL_DB_DIR

conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "aspas.db"))
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    student_name TEXT,
    student_code TEXT,
    section TEXT,
    department TEXT,
    batch_code TEXT,
    semester INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chatbot_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL CHECK(sender IN ('user', 'bot')),
    message_text TEXT NOT NULL,
    message_type TEXT DEFAULT 'text' CHECK(message_type IN ('text', 'voice')),
    detected_intent TEXT,
    response_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
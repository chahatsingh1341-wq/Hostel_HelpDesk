import sqlite3
from datetime import datetime

DB_NAME = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Credentials table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL
    )
    """)
    
    # Complaints table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        user_type TEXT NOT NULL,
        block TEXT NOT NULL,
        floor TEXT NOT NULL,
        corridor TEXT NOT NULL,
        room TEXT,
        issue_type TEXT NOT NULL,
        issue_category TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)
    
    # Feedback table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        user_type TEXT NOT NULL,
        rating INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

def insert_credential(email, password, user_type):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO credentials (email, password, user_type) VALUES (?, ?, ?)",
            (email, password, user_type)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_credential(email, password, user_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM credentials WHERE email=? AND password=? AND user_type=?",
        (email, password, user_type)
    )
    user = cur.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM credentials WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()
    return user

def insert_complaint(user_email, user_type, block, floor, corridor, room, issue_type, issue_category, created_at):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO complaints (user_email, user_type, block, floor, corridor, room, issue_type, issue_category, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_email, user_type, block, floor, corridor, room, issue_type, issue_category, created_at))
    conn.commit()
    conn.close()

def get_all_complaints():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints ORDER BY id DESC")
    complaints = cur.fetchall()
    conn.close()
    return complaints

def get_user_complaints(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints WHERE user_email=? ORDER BY id DESC", (email,))
    complaints = cur.fetchall()
    conn.close()
    return complaints

def insert_feedback(user_email, user_type, rating, message, created_at):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO feedback (user_email, user_type, rating, message, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (user_email, user_type, rating, message, created_at))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feedback ORDER BY id DESC")
    feedbacks = cur.fetchall()
    conn.close()
    return feedbacks

def update_complaint_status(cid, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET status=? WHERE id=?", (status, cid))
    conn.commit()
    conn.close()

def delete_old_resolved_complaints():
    conn = get_connection()
    cur = conn.cursor()
    
    # Delete resolved complaints older than 30 days
    cur.execute("""
    DELETE FROM complaints 
    WHERE status='Resolved' 
    AND created_at < ?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M"),))
    
    deleted_count = cur.rowcount
    conn.commit()
    conn.close()
    return deleted_count
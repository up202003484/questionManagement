import sqlite3
import pickle
import os
import time
from utils.helper import current_timestamp, convert_to_human_readable
import shutil

# Path to your SQLite database
DB_PATH = 'backlog.db'



def get_connection():
    """Establish and return a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    return conn



def update_question_prio(question_id, new_priority):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE questions
        SET priority = ?
        WHERE id = ?
    """, (new_priority, question_id))
    conn.commit()
    conn.close()

def update_question_status(question_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE questions
        SET status = ?
        WHERE id = ?
    """, (new_status, question_id))
    conn.commit()
    conn.close()

def remove_question(question_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM questions
        WHERE id = ?
    """, (question_id,))
    conn.commit()
    conn.close()

def create_questions_table():
    """Creates the questions table if it doesn't already exist."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        owner TEXT NOT NULL,
        status TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        created_at TEXT NOT NULL,
        embedding BLOB NOT NULL,
        discussion TEXT,
        taxonomy TEXT
    )
    ''')
    connection.commit()
    connection.close()

def create_discussions_table():
    """Creates the discussions table if it doesn't already exist."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        author TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    ''')
    connection.commit()
    connection.close()

create_discussions_table()
create_questions_table()

def load_backlog():
    """Load all questions from the backlog database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()
    conn.close()
    
    backlog = []
    for row in rows:
        # Deserialize the embedding from BLOB to list of floats
        embedding = pickle.loads(row[7])  # Convert BLOB back to list
        created_at = convert_to_human_readable(row[6])
        question = {
            "id": row[0],
            "question": row[1],
            "owner": row[2],
            "status": row[3],
            "category": row[4],
            "priority": row[5],
            "created_at": created_at,
            "embedding": embedding,
            "discussion": get_discussion_by_question_id(row[0]),
            "taxonomy": row[9],  # assuming it's the 9th column
        }
        backlog.append(question)
    
    return backlog

def get_discussion_by_question_id(question_id):
    """Retrieve all discussion messages for a specific question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM discussions WHERE question_id = ? ORDER BY created_at", (question_id,))
    rows = cursor.fetchall()
    conn.close()

    discussion = []
    for row in rows:
        message = {
            "source": row[2],  # 'user' or 'ai'
            "message": row[3],
            "created_at": row[4]
        }
        discussion.append(message)
    
    return discussion

def update_discussion(question_id, author, message):
    """Add a message to the discussion for a specific question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO discussions (question_id, author, message, created_at)
                      VALUES (?, ?, ?, ?)""", 
                   (question_id, author, message, current_timestamp()))
    conn.commit()
    conn.close()


def save_to_backlog(new_question):
    """Save a new question to the backlog database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Serialize the embedding (list of floats) into a binary format
    embedding_blob = pickle.dumps(new_question["embedding"])  # Convert list to binary
    
    query = """INSERT INTO questions (question, owner, status, category, priority, created_at, embedding, taxonomy)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    try:
        cursor.execute(query, (
            new_question["question"],
            new_question["owner"],
            new_question["status"],
            new_question["category"],
            new_question["priority"],
            new_question["created_at"],
            embedding_blob,  # Save the serialized embedding as BLOB
            new_question.get("taxonomy", "")
        ))
        conn.commit()
    except sqlite3.ProgrammingError as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

def add_to_discussion(question_id, author, message):
    """Add a message to the discussion for a specific question."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """INSERT INTO discussions (question_id, author, message, created_at)
               VALUES (?, ?, ?, ?)"""
    cursor.execute(query, (
        question_id,
        author,
        message,
        current_timestamp()  # Current timestamp for when the message was added
    ))
    conn.commit()
    conn.close()

def get_discussion_by_question_id(question_id):
    """Retrieve all discussion messages for a specific question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM discussions WHERE question_id = ? ORDER BY created_at", (question_id,))
    rows = cursor.fetchall()
    conn.close()

    discussion = []
    for row in rows:
        message = {
            "source": row[2],  # 'user' or 'ai'
            "message": row[3],
            "created_at": row[4]
        }
        discussion.append(message)
    
    return discussion


def clear_backlog():
    """Remove all questions from the backlog database."""
    import sqlite3
    conn = sqlite3.connect("backlog.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions")
    cursor.execute("DELETE FROM discussions")
    # Optionally, you can also reset the auto-increment ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='questions'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='discussions'")
    conn.commit()
    conn.close()

def clear_discussion_for_question(question_id):
    import sqlite3
    conn = sqlite3.connect("backlog.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM discussions WHERE question_id = ?", (question_id,))
    conn.commit()
    conn.close()

def get_last_saved_question():
    """Fetch the last saved question from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Deserialize the embedding from BLOB to list of floats
        embedding = pickle.loads(row[7])  # Convert BLOB back to list
        question = {
            "id": row[0],
            "question": row[1],
            "owner": row[2],
            "status": row[3],
            "category": row[4],
            "priority": row[5],
            "created_at": row[6],
            "embedding": embedding,
            "taxonomy": row[9],
        }
        return question
    else:
        return None
    

def ensure_snapshot_dir():
    os.makedirs("snapshots", exist_ok=True)

def get_next_snapshot_filename():
    ensure_snapshot_dir()
    existing = os.listdir("snapshots")
    count = len([f for f in existing if f.startswith("backlog_q") and f.endswith(".db")])
    return f"snapshots/backlog_q{count+1:03d}.db"

def create_snapshot():
    """Create a backup of the main backlog.db as a snapshot."""
    snapshot_path = get_next_snapshot_filename()
    shutil.copyfile("backlog.db", snapshot_path)
    return snapshot_path
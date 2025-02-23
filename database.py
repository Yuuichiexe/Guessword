import sqlite3

DATABASE = 'scores.db'

def get_connection():
    # Use check_same_thread=False if you plan to access the connection from multiple threads.
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Optional: for dict-like row access
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Create table for global scores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_scores (
                user_id INTEGER PRIMARY KEY,
                score INTEGER NOT NULL DEFAULT 0
            )
        ''')
        # Create table for chat-specific scores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_scores (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        ''')
        conn.commit()

def update_global_score(user_id, points=1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO global_scores (user_id, score)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET score = score + ?
        ''', (user_id, points, points))
        conn.commit()

def update_chat_score(chat_id, user_id, points=1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_scores (chat_id, user_id, score)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET score = score + ?
        ''', (chat_id, user_id, points, points))
        conn.commit()

def get_global_leaderboard(limit=10):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, score FROM global_scores 
            ORDER BY score DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

def get_chat_leaderboard(chat_id, limit=10):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, score FROM chat_scores 
            WHERE chat_id = ? 
            ORDER BY score DESC 
            LIMIT ?
        ''', (chat_id, limit))
        return cursor.fetchall()

# Initialize the database (create tables if they don't exist)
if __name__ == 'database':
    init_db()

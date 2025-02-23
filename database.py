import sqlite3

# Connect to the database (creates a new file if it doesn't exist)
conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_scores (
        user_id INTEGER PRIMARY KEY,
        score INTEGER DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_scores (
        chat_id INTEGER,
        user_id INTEGER,
        score INTEGER DEFAULT 0,
        PRIMARY KEY (chat_id, user_id)
    )
""")

conn.commit()

# Function to update global score
def update_global_score(user_id):
    cursor.execute("INSERT INTO global_scores (user_id, score) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET score = score + 1", (user_id,))
    conn.commit()

# Function to update chat score
def update_chat_score(chat_id, user_id):
    cursor.execute("INSERT INTO chat_scores (chat_id, user_id, score) VALUES (?, ?, 1) ON CONFLICT(chat_id, user_id) DO UPDATE SET score = score + 1", (chat_id, user_id))
    conn.commit()

# Function to get global leaderboard
def get_global_leaderboard():
    cursor.execute("SELECT user_id, score FROM global_scores ORDER BY score DESC LIMIT 10")
    return cursor.fetchall()

# Function to get chat leaderboard
def get_chat_leaderboard(chat_id):
    cursor.execute("SELECT user_id, score FROM chat_scores WHERE chat_id = ? ORDER BY score DESC LIMIT 10", (chat_id,))
    return cursor.fetchall()


app = Client("word_guess_bot", bot_token=7560532835:AAFhlP0P_WCtsbBjwBgQMT7cWU3ht_xE598, api_id=20222660, api_hash=5788f1f4a93f2de28835a0cf1b0ebae4)
app.start()
app.storage.conn.execute("PRAGMA journal_mode=WAL;")
app.storage.conn.timeout = 30
app.stop()
# Now start the bot normally
app.run()

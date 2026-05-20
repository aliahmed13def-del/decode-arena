import sqlite3

def get_db():
    conn = sqlite3.connect('hunt.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        trail TEXT NOT NULL,
        score REAL DEFAULT 0,
        puzzles_solved INTEGER DEFAULT 0,
        current_stage INTEGER DEFAULT 1,
        disqualified INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS puzzles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail TEXT NOT NULL,
        stage INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        points REAL DEFAULT 10,
        hint TEXT,
        is_physical INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        stage INTEGER NOT NULL,
        answer_given TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Timer table — controls the event countdown
    c.execute('''CREATE TABLE IF NOT EXISTS event_control (
        id INTEGER PRIMARY KEY,
        status TEXT DEFAULT 'waiting',
        started_at TIMESTAMP,
        duration_seconds INTEGER DEFAULT 10800,
        ended_at TIMESTAMP
    )''')

    # Insert default event control row if not exists
    c.execute('''INSERT OR IGNORE INTO event_control
                 (id, status, duration_seconds)
                 VALUES (1, 'waiting', 10800)''')

    conn.commit()
    conn.close()
    print("Database ready!")
import sqlite3
import os

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS env_variables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                )
            ''')

    def save_env_variables(self, google_nest_clipper_prefs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for key, value in google_nest_clipper_prefs.items():
                cursor.execute("INSERT OR REPLACE INTO env_variables (key, value) VALUES (?, ?)", (key, value))

    def get_env_variables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM env_variables")
            return dict(cursor.fetchall())


def get_db_path():
    if os.name.lower() == 'nt':  # Windows
        return os.path.join(os.getenv('APPDATA'), 'GoogleNestClipper', 'google_nest_clipper_prefs.db')
    elif 'darwin' in os.uname().sysname.lower():  # macOS
        return os.path.join(os.path.expanduser('~/Library/Application Support/GoogleNestClipper'), 'google_nest_clipper_prefs.db')
    else:  # Linux
        return os.path.join(os.path.expanduser('~/.config/GoogleNestClipper'), 'google_nest_clipper_prefs.db')

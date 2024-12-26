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
                CREATE TABLE IF NOT EXISTS app_prefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                )
            ''')

    def save_app_prefs(self, google_nest_clipper_prefs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for key, value in google_nest_clipper_prefs.items():
                cursor.execute("INSERT OR REPLACE INTO app_prefs (key, value) VALUES (?, ?)", (key, value))

    def get_app_prefs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM app_prefs")
            return dict(cursor.fetchall())
        
    def get_master_token_creation_date(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_prefs WHERE key ='MASTER_TOKEN_CREATION_DATE'")
            return cursor.fetchone()[0]
        
    def get_master_token(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_prefs WHERE key ='GOOGLE_MASTER_TOKEN'")
            return cursor.fetchone()[0]


def get_db_path():
    # Windows
    if os.name.lower() == 'nt': 
        return os.path.join(os.getenv('APPDATA'), 'GoogleNestClipper', 'google_nest_clipper_prefs.db')
    
    # MacOs
    elif 'darwin' in os.uname().sysname.lower():
        return os.path.join(os.path.expanduser('~/Library/Application Support/GoogleNestClipper'), 'google_nest_clipper_prefs.db')
    
    # Linux
    else:
        return os.path.join(os.path.expanduser('~/.config/GoogleNestClipper'), 'google_nest_clipper_prefs.db')

def check_database_exists():
    # Replace 'path_to_secure_db' with the actual path to your secure database file
    db_path = get_db_path()
    return os.path.exists(db_path)
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from dotenv import load_dotenv
import main
from tools import logger


class GoogleNestClipperApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.refresh_interval = 3600  # Default refresh interval is 1 hour (3600 seconds)
        self.timer_thread = None

        self.root.title("Google Nest Clipper")
        self.root.geometry("500x500")

        # Set up the database path
        if os.name.lower() == 'nt':  # Windows
            self.db_path = os.path.join(os.getenv('APPDATA'), 'GoogleNestClipper', 'env_vars.db')
        else:  # Non-Windows systems
            self.db_path = os.path.join(os.path.expanduser('~/.config/GoogleNestClipper'), 'env_vars.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize UI components and load environment variables
        self.initialize_ui()
        self.load_env_variables()

        # Bind the close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_ui(self):
        tk.Label(self.root, text="Email:", font=("Arial", 15)).pack(pady=10)
        self.email_entry = tk.Entry(self.root, width=40, font=("Arial", 15))
        self.email_entry.pack(pady=5)

        tk.Label(self.root, text="Master Token:", font=("Arial", 15)).pack(pady=10)
        self.master_token_entry = tk.Entry(self.root, show="*", width=40, font=("Arial", 15))
        self.master_token_entry.pack(pady=5)

        tk.Label(self.root, text="Video Save Path:", font=("Arial", 15)).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack()

        self.video_save_path_entry = tk.Entry(frame, width=27, font=("Arial", 15), state='readonly')
        self.video_save_path_entry.pack(side=tk.LEFT, padx=5)

        browse_button = tk.Button(frame, text="Browse...", command=self.select_save_path, font=("Arial", 16), height=1, width=10)
        browse_button.pack(side=tk.RIGHT, padx=5)

        tk.Label(self.root, text="Time to Refresh (in seconds):", font=("Arial", 15)).pack(pady=10)
        self.time_to_refresh_entry = tk.Entry(self.root, width=40, font=("Arial", 15))
        self.time_to_refresh_entry.pack(pady=5)

        self.start_stop_button = tk.Button(self.root, text="Start", command=self.toggle_running_state, font=("Arial", 16), height=2, width=10)
        self.start_stop_button.pack(pady=20)

    def load_env_variables(self):
        """Load environment variables from the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS env_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')

        cursor.execute("SELECT key, value FROM env_variables")
        rows = cursor.fetchall()

        for row in rows:
            key, value = row
            if key == "GOOGLE_USERNAME":
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, value)
            elif key == "GOOGLE_MASTER_TOKEN":
                self.master_token_entry.delete(0, tk.END)
                self.master_token_entry.insert(0, value)
            elif key == "VIDEO_SAVE_PATH":
                self.video_save_path_entry.config(state='normal')
                self.video_save_path_entry.delete(0, tk.END)
                self.video_save_path_entry.insert(0, value)
                self.video_save_path_entry.config(state='readonly')
            elif key == "TIME_TO_REFRESH":
                self.time_to_refresh_entry.delete(0, tk.END)
                self.time_to_refresh_entry.insert(0, value)
                self.refresh_interval = int(value)

        conn.close()

    def on_closing(self):
        """Handle window close event."""
        self.running = False
        if self.timer_thread:
            self.timer_thread.cancel()
        self.root.destroy()

    def select_save_path(self):
        """Open a file dialog to select a directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.video_save_path_entry.config(state='normal')
            self.video_save_path_entry.delete(0, tk.END)
            self.video_save_path_entry.insert(0, directory)
            self.video_save_path_entry.config(state='readonly')

    def save_env_file(self):
        """Save environment variables to the SQLite database."""
        email = self.email_entry.get()
        master_token = self.master_token_entry.get()
        video_save_path = self.video_save_path_entry.get()
        time_to_refresh = self.time_to_refresh_entry.get()

        if not email or not master_token or not video_save_path:
            messagebox.showerror("Error", "All fields are required.")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS env_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')

        env_vars = [
            ("GOOGLE_USERNAME", email),
            ("GOOGLE_MASTER_TOKEN", master_token),
            ("VIDEO_SAVE_PATH", video_save_path),
            ("TIME_TO_REFRESH", str(time_to_refresh))
        ]

        for key, value in env_vars:
            cursor.execute("INSERT OR REPLACE INTO env_variables (key, value) VALUES (?, ?)", (key, value))

        conn.commit()
        conn.close()
        self.load_env_variables()
        return True

    def toggle_running_state(self):
        """Toggle between Running and Non-Running states."""
        if self.running:
            self.running = False
            self.start_stop_button.config(text="Start")
            self.set_fields_state("normal")
            if self.timer_thread:
                self.timer_thread.cancel()
        else:
            # Automatically save before starting
            if self.save_env_file():
                self.running = True
                self.start_stop_button.config(text="Stop")
                self.set_fields_state("readonly")
                self.start_periodic_task()

    def set_fields_state(self, state):
        """Set the state of editable fields."""
        self.email_entry.config(state=state)
        self.master_token_entry.config(state=state)
        self.time_to_refresh_entry.config(state=state)

    def start_periodic_task(self):
        """Start the periodic task."""
        if self.timer_thread:
            self.timer_thread.cancel()

        def task():
            if self.running:
                try:
                    main.main(
                        os.getenv("GOOGLE_MASTER_TOKEN"),
                        os.getenv("GOOGLE_USERNAME"),
                        os.getenv("VIDEO_SAVE_PATH")
                    )
                except Exception as e:
                    logger.error(f"Error running main function: {e}")
                finally:
                    if self.running:
                        self.timer_thread = threading.Timer(self.refresh_interval, task)
                        self.timer_thread.start()

        task()


if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleNestClipperApp(root)
    root.mainloop()

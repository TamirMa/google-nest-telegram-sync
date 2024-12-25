import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from app_prefs_database import DatabaseHandler, get_db_path
from google_nest_clipper import main

class GoogleNestClipperApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.refresh_interval = None
        self.timer_thread = None
        self.db_handler = DatabaseHandler(get_db_path())

        self.root.title("Google Nest Clipper")
        self.root.geometry("500x500")
        self.initialize_ui()
        self.load_env_variables()
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
        tk.Button(frame, text="Browse...", command=self.select_save_path, font=("Arial", 16), height=1, width=10).pack(side=tk.RIGHT, padx=5)

        tk.Label(self.root, text="Time to Refresh (in seconds):", font=("Arial", 15)).pack(pady=10)
        self.time_to_refresh_entry = tk.Entry(self.root, width=40, font=("Arial", 15))
        self.time_to_refresh_entry.pack(pady=5)

        self.start_stop_button = tk.Button(self.root, text="Start", command=self.toggle_running_state, font=("Arial", 16), height=2, width=10)
        self.start_stop_button.pack(pady=20)

    def load_env_variables(self):
        google_nest_clipper_prefs = self.db_handler.get_env_variables()
        if google_nest_clipper_prefs:
            self.email_entry.insert(0, google_nest_clipper_prefs.get("GOOGLE_USERNAME", ""))
            self.master_token_entry.insert(0, google_nest_clipper_prefs.get("GOOGLE_MASTER_TOKEN", ""))
            self.video_save_path_entry.config(state='normal')
            self.video_save_path_entry.insert(0, google_nest_clipper_prefs.get("VIDEO_SAVE_PATH", ""))
            self.video_save_path_entry.config(state='readonly')
            self.time_to_refresh_entry.insert(0, google_nest_clipper_prefs.get("TIME_TO_REFRESH"))
            self.refresh_interval = int(google_nest_clipper_prefs.get("TIME_TO_REFRESH"))

    def on_closing(self):
        self.running = False
        if self.timer_thread:
            self.timer_thread.cancel()
        self.root.destroy()

    def select_save_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.video_save_path_entry.config(state='normal')
            self.video_save_path_entry.delete(0, tk.END)
            self.video_save_path_entry.insert(0, directory)
            self.video_save_path_entry.config(state='readonly')

    def save_env_variables(self):
        email = self.email_entry.get()
        master_token = self.master_token_entry.get()
        video_save_path = self.video_save_path_entry.get()
        time_to_refresh = self.time_to_refresh_entry.get()

        if not email or not master_token or not video_save_path or not time_to_refresh:
            messagebox.showerror("Error", "All fields are required.")
            return False

        google_nest_clipper_prefs = {
            "GOOGLE_USERNAME": email,
            "GOOGLE_MASTER_TOKEN": master_token,
            "VIDEO_SAVE_PATH": video_save_path,
            "TIME_TO_REFRESH": time_to_refresh
        }
        self.db_handler.save_env_variables(google_nest_clipper_prefs)
        return True

    def toggle_running_state(self):
        if self.running:
            self.running = False
            self.start_stop_button.config(text="Start")
            self.set_fields_state("normal")
            if self.timer_thread:
                self.timer_thread.cancel()
        else:
            if self.save_env_variables():
                self.running = True
                self.start_stop_button.config(text="Stop")
                self.set_fields_state("readonly")
                self.start_periodic_task()

    def set_fields_state(self, state):
        self.email_entry.config(state=state)
        self.master_token_entry.config(state=state)
        self.time_to_refresh_entry.config(state=state)

    def start_periodic_task(self):
        def task():
            if self.running:
                # Reload the latest environment variables
                google_nest_clipper_prefs = self.db_handler.get_env_variables()

                # Pass the updated variables to the main function
                main(
                    google_nest_clipper_prefs.get("GOOGLE_MASTER_TOKEN", ""),
                    google_nest_clipper_prefs.get("GOOGLE_USERNAME", ""),
                    google_nest_clipper_prefs.get("VIDEO_SAVE_PATH", "")
                )

                # Update the refresh interval dynamically
                self.refresh_interval = int(google_nest_clipper_prefs.get("TIME_TO_REFRESH", self.refresh_interval))

                # Schedule the next run
                if self.running:
                    self.timer_thread = threading.Timer(self.refresh_interval, task)
                    self.timer_thread.start()

        task()

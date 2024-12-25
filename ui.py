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
        self.running = True
        self.refresh_interval = 3600
        self.timer_thread = None

        self.root.title("Google Nest Clipper")
        self.root.geometry("500x400")

        # Initialize UI components and env vars on startup
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
        self.video_save_path_entry = tk.Entry(self.root, width=40, font=("Arial", 15), state='readonly')
        self.video_save_path_entry.pack(pady=5)

        tk.Button(self.root, text="Browse...", command=self.select_save_path, font=("Arial", 16), height=1, width=10).pack(pady=5)

        tk.Button(self.root, text="Save", command=self.save_env_file, font=("Arial", 16), height=2, width=10).pack(pady=20)

    def load_env_variables(self):
        """Load environment variables from a .env file."""
        if os.path.exists(".env"):
            load_dotenv()
            email = os.getenv("GOOGLE_USERNAME")
            master_token = os.getenv("GOOGLE_MASTER_TOKEN")
            video_save_path = os.getenv("VIDEO_SAVE_PATH")
            self.refresh_interval = int(os.getenv("TIME_TO_REFRESH"))

            # Set the entry fields
            if email:
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, email)
            if master_token:
                self.master_token_entry.delete(0, tk.END)
                self.master_token_entry.insert(0, master_token)
            if video_save_path:
                self.video_save_path_entry.config(state='normal')
                self.video_save_path_entry.delete(0, tk.END)
                self.video_save_path_entry.insert(0, video_save_path)
                self.video_save_path_entry.config(state='readonly')
    
    def on_closing(self):
        "Handle window close event."
        self.running = False
        if self.timer_thread:
            self.timer_thread.cancel()
        self.root.destroy()

    def select_save_path(self):
        "Open a file dialog to select a directory."
        directory = filedialog.askdirectory()
        if directory:
            self.video_save_path_entry.config(state='normal')
            self.video_save_path_entry.delete(0, tk.END)
            self.video_save_path_entry.insert(0, directory)
            self.video_save_path_entry.config(state='readonly')

    def save_env_file(self):
        "Save environment variables to a .env file."
        email = self.email_entry.get()
        master_token = self.master_token_entry.get()
        video_save_path = self.video_save_path_entry.get()

        if not email or not master_token or not video_save_path:
            messagebox.showerror("Error", "All fields are required.")
            return

        env_content = (
            f'GOOGLE_MASTER_TOKEN="{master_token}"\n'
            f'GOOGLE_USERNAME="{email}"\n'
            f'VIDEO_SAVE_PATH="{video_save_path}"\n'
            f'TIME_TO_REFRESH="{self.refresh_interval}"\n'
        )

        with open(".env", "w") as file:
            file.write(env_content)

        # Update refresh interval from the saved file
        self.load_env_variables()

        # Start periodic task
        self.start_periodic_task()

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

        # Start the first execution
        task()


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleNestClipperApp(root)
    root.mainloop()

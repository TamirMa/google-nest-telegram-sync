import datetime
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from app_prefs_database import DatabaseHandler, get_db_path
from nest_clipper import main

class NestClipperApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.refresh_interval = None
        self.timer_thread = None
        self.db_handler = DatabaseHandler(get_db_path())

        self.root.title("Nest Clipper")
        self.root.geometry("570x330")
        self.root.configure(bg="#f2f2f2")
        self.initialize_ui()
        self.load_app_prefs()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_ui(self):
        # Title Label
        title_label = tk.Label(
            self.root,
            text="Nest Clipper",
            font=("Helvetica", 18, "bold"),
            fg="#333333",
            bg="#f2f2f2",
            pady=10,
        )
        title_label.pack()

        # Main Frame for Form
        form_frame = tk.Frame(self.root, bg="#f2f2f2", padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        # Email (Read-only)
        tk.Label(form_frame, text="Email:", font=("Arial", 12), bg="#f2f2f2").grid(
            row=0, column=0, sticky="w", pady=10
        )
        self.email_entry = tk.Entry(form_frame, width=40, font=("Arial", 12), state="readonly")
        self.email_entry.grid(row=0, column=1, pady=10)

        # Video Save Path
        tk.Label(
            form_frame, text="Video Save Path:", font=("Arial", 12), bg="#f2f2f2"
        ).grid(row=1, column=0, sticky="w", pady=10)
        path_frame = tk.Frame(form_frame, bg="#f2f2f2")
        path_frame.grid(row=1, column=1, sticky="w")
        self.video_save_path_entry = tk.Entry(
            path_frame, width=30, font=("Arial", 12), state="readonly"
        )
        self.video_save_path_entry.pack(side=tk.LEFT, padx=5)
        self.browse_button = tk.Button(
            path_frame,
            text="Browse...",
            command=self.select_save_path,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
        )
        self.browse_button.pack(side=tk.RIGHT)

        # Time to Refresh
        tk.Label(
            form_frame, text="Refresh Freq (sec):", font=("Arial", 12), bg="#f2f2f2"
        ).grid(row=2, column=0, sticky="w", pady=10)
        self.time_to_refresh_entry = tk.Entry(form_frame, width=40, font=("Arial", 12))
        self.time_to_refresh_entry.grid(row=2, column=1, pady=10)

        # Start/Stop Button
        self.start_stop_button = tk.Button(
            self.root,
            text="Start",
            command=self.toggle_running_state,
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2,
            width=12,
        )
        self.start_stop_button.pack(pady=20)

        # Logout Button
        logout_button = tk.Button(
            self.root,
            text="Logout",
            command=self.logout,
            font=("Arial", 12),
            bg="#FF5733",
            fg="white",
        )
        logout_button.place(relx=0.95, rely=0.95, anchor="se")  # Bottom right corner

    def load_app_prefs(self):
        nest_clipper_prefs = self.db_handler.get_app_prefs()
        if nest_clipper_prefs:
            self.email_entry.config(state="normal")
            self.email_entry.insert(0, nest_clipper_prefs.get("USERNAME", ""))
            self.email_entry.config(state="readonly")
            self.video_save_path_entry.config(state="normal")
            self.video_save_path_entry.insert(0, nest_clipper_prefs.get("VIDEO_SAVE_PATH", ""))
            self.video_save_path_entry.config(state="readonly")
            self.time_to_refresh_entry.insert(0, nest_clipper_prefs.get("TIME_TO_REFRESH"))
            self.refresh_interval = int(nest_clipper_prefs.get("TIME_TO_REFRESH"))

    def logout(self):
        if messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to log out? Frequent Logging out may lead Google to disconnect your android devices and other weird things may happen.",
        ):
            try:
                self.db_handler.delete_table()
                self.root.destroy()
                import pre_auth_app_ui
                root = tk.Tk()
                app = pre_auth_app_ui.PreAuthNestClipperApp(root)
                root.mainloop()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to log out: {str(e)}")

    def on_closing(self):
        self.running = False
        if self.timer_thread:
            self.timer_thread.cancel()
        self.root.destroy()

    def select_save_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.video_save_path_entry.config(state="normal")
            self.video_save_path_entry.delete(0, tk.END)
            self.video_save_path_entry.insert(0, directory)
            self.video_save_path_entry.config(state="readonly")

    def save_app_prefs(self):
        email = self.email_entry.get()
        video_save_path = self.video_save_path_entry.get()
        time_to_refresh = self.time_to_refresh_entry.get()

        if not email or not video_save_path or not time_to_refresh:
            messagebox.showerror("Error", "All fields are required.")
            return False

        nest_clipper_prefs = {
            "USERNAME": email,
            "VIDEO_SAVE_PATH": video_save_path,
            "TIME_TO_REFRESH": time_to_refresh,
        }
        self.db_handler.save_app_prefs(nest_clipper_prefs)
        return True

    def toggle_running_state(self):
        if self.running:
            self.running = False
            self.start_stop_button.config(text="Start", bg="#4CAF50")
            self.set_fields_state("normal")
            if self.timer_thread:
                self.timer_thread.cancel()
        else:
            if self.save_app_prefs():
                self.running = True
                self.start_stop_button.config(text="Stop", bg="#FF5733")
                self.set_fields_state("readonly")
                self.start_periodic_task()

    def set_fields_state(self, state):
        self.time_to_refresh_entry.config(state=state)
        if state == "readonly":
            self.browse_button.config(state="disabled", bg="#312f2f")
        else:
            self.browse_button.config(state="normal", bg="#4CAF50")

    def start_periodic_task(self):
        def task():
            if self.running:
                nest_clipper_prefs = self.db_handler.get_app_prefs()
                main(
                    nest_clipper_prefs.get("MASTER_TOKEN", ""),
                    nest_clipper_prefs.get("USERNAME", ""),
                    nest_clipper_prefs.get("VIDEO_SAVE_PATH", ""),
                )
                self.refresh_interval = int(
                    nest_clipper_prefs.get("TIME_TO_REFRESH", self.refresh_interval)
                )
                if self.running:
                    self.timer_thread = threading.Timer(self.refresh_interval, task)
                    self.timer_thread.start()

        task()

if __name__ == "__main__":
    root = tk.Tk()
    app = NestClipperApp(root)
    root.mainloop()

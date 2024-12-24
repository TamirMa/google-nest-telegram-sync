import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
from dotenv import load_dotenv

# Add main.py to the system path so we can import the main function
sys.path.append(os.path.dirname(__file__))
import main

def select_save_path():
    directory = filedialog.askdirectory()
    if directory:
        video_save_path_entry.config(state='normal')  # Make the entry editable temporarily
        video_save_path_entry.delete(0, tk.END)
        video_save_path_entry.insert(0, directory)
        video_save_path_entry.config(state='readonly')  # Make the entry read-only again

def save_env_file():
    email = email_entry.get()
    master_token = master_token_entry.get()
    video_save_path = video_save_path_entry.get()

    if not email or not master_token or not video_save_path:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Write to the .env file with no trailing newline for VIDEO_SAVE_PATH
    env_content = (
        f'GOOGLE_MASTER_TOKEN="{master_token}"\n'
        f'GOOGLE_USERNAME="{email}"\n'
        f'VIDEO_SAVE_PATH="{video_save_path}"\n'
    )

    with open(".env", "w") as file:
        file.write(env_content)

    # Run the main function from main.py
    main.main(master_token, email, video_save_path)

def load_env_variables():
    if os.path.exists(".env"):
        load_dotenv()
        email = os.getenv("GOOGLE_USERNAME")
        master_token = os.getenv("GOOGLE_MASTER_TOKEN")
        video_save_path = os.getenv("VIDEO_SAVE_PATH")
        
        # Set the entry fields with values from .env
        if email:
            email_entry.insert(0, email)
        if master_token:
            master_token_entry.insert(0, master_token)
        if video_save_path:
            video_save_path_entry.config(state='normal')
            video_save_path_entry.delete(0, tk.END)  # Clear any existing value
            video_save_path_entry.insert(0, video_save_path)
            video_save_path_entry.config(state='readonly')

# Create the main window
root = tk.Tk()
root.title("Google Nest Clipper")
root.geometry("500x400")  # Set initial size of the window

# Email Entry
email_label = tk.Label(root, text="Email:", font=("Arial", 15))
email_label.pack(pady=10)
email_entry = tk.Entry(root, width=40, font=("Arial", 15))
email_entry.pack(pady=5)

# Master Token Entry
master_token_label = tk.Label(root, text="Master Token:", font=("Arial", 15))
master_token_label.pack(pady=10)
master_token_entry = tk.Entry(root, show="*", width=40, font=("Arial", 15))
master_token_entry.pack(pady=5)

# Video Save Path Entry
video_save_path_label = tk.Label(root, text="Video Save Path:", font=("Arial", 15))
video_save_path_label.pack(pady=10)
video_save_path_entry = tk.Entry(root, width=40, font=("Arial", 15), state='readonly')
video_save_path_entry.pack(pady=5)

# File Browser Button
file_browser_button = tk.Button(root, text="Browse...", command=select_save_path, font=("Arial", 16), height=1, width=10)
file_browser_button.pack(pady=5)

# Save Button
save_button = tk.Button(root, text="Save", command=save_env_file, font=("Arial", 16), height=2, width=10)
save_button.pack(pady=20)

# Load environment variables on startup
load_env_variables()

# Run the application
root.mainloop()

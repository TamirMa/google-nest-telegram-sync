import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from app_prefs_database import DatabaseHandler, get_db_path
from glocaltokens.client import GLocalAuthenticationTokens

class PreAuthGoogleNestClipperApp:
  def __init__(self, root):
    self.root = root
    self.email_entry = None
    self.app_password_entry = None
    self.db_handler = None
    self.setup_ui()

  def setup_ui(self):
    self.root.title("Google Nest Clipper")
    self.root.geometry("300x130")

    tk.Label(self.root, text="Email:").pack()
    self.email_entry = tk.Entry(self.root)
    self.email_entry.pack()

    tk.Label(self.root, text="App Password:").pack()
    self.app_password_entry = tk.Entry(self.root, show='*')
    self.app_password_entry.pack()

    tk.Button(self.root, text="Authenticate", command=self.authenticate).pack()

  def authenticate(self):
    email = self.email_entry.get()
    app_password = self.app_password_entry.get()

    if not email or not app_password:
      messagebox.showerror("Error", "Both Email and App Password are required.")
      return

    try:
      client = GLocalAuthenticationTokens(
        username=email,
        password=app_password
      )
      
      master_token = client.get_master_token()

      if not master_token:
        messagebox.showerror("Error", "Invalid Credentials.")
        return

      if self.db_handler is None:
        self.db_handler = DatabaseHandler(get_db_path())

      google_nest_clipper_prefs = {
        "GOOGLE_USERNAME": email,
        "GOOGLE_MASTER_TOKEN": master_token,
        "MASTER_TOKEN_CREATION_DATE": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "VIDEO_SAVE_PATH": "",
        "TIME_TO_REFRESH": "3600"
      }

      self.db_handler.save_app_prefs(google_nest_clipper_prefs)
      messagebox.showinfo("Success", "Master Token saved successfully. Starting the application.")

      self.root.destroy()
      import auth_app_ui
      root = tk.Tk()
      app = auth_app_ui.GoogleNestClipperApp(root)
      root.mainloop()

    except Exception as e:
      messagebox.showerror("Error", f"Failed to authenticate: {str(e)}")

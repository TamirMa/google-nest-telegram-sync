import tkinter as tk
from app_prefs_database import check_database_exists
from auth_app_ui import GoogleNestClipperApp
from pre_auth_app_ui import PreAuthGoogleNestClipperApp

if __name__ == "__main__":
    root = tk.Tk()

    if check_database_exists(): # this should also check if master token is valid. not sure how to do that
        app = GoogleNestClipperApp(root)
        root.mainloop()

    else:
        app = PreAuthGoogleNestClipperApp(root)
        root.mainloop()

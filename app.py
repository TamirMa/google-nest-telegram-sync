import os
import sys
import tkinter as tk
from app_prefs_database import check_database_exists
from auth_app_ui import NestClipperApp
from pre_auth_app_ui import PreAuthNestClipperApp

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    icon_path = resource_path("resources/Nest Clipper Logo.png")
    icon_image = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, icon_image)

    if check_database_exists(): # this should also check if master token is valid. not sure how to do that
        app = NestClipperApp(root)
        root.mainloop()

    else:
        app = PreAuthNestClipperApp(root)
        root.mainloop()

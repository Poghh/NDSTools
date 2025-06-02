import os
import sys
import time
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# GUI imports
from tkinterdnd2 import TkinterDnD
from tkinter import ttk
from toolsUI.beTab.ui_be import BackEndTab
from toolsUI.ui_fe import FrontEndTab


# ========== Watchdog Handler ==========
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_modified(self, event):
        src_path = (
            event.src_path.decode()
            if isinstance(event.src_path, bytes)
            else event.src_path
        )
        if src_path.endswith(".py"):
            print(f"🔁 File changed: {src_path}, reloading app...")
            self.restart_callback()


# ========== Main App ==========
class AutoReviewTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Review Tool")
        self.root.geometry("1200x780")

        self.tab_parent = ttk.Notebook(self.root)
        self.tab_parent.pack(fill="both", expand=True)

        # Tạo tab FE
        self.fe_tab = FrontEndTab(self.tab_parent)

        # Tạo tab BE
        self.be_tab = BackEndTab(self.tab_parent)


# ========== Reload Logic ==========
def launch_gui():
    global root
    root = TkinterDnD.Tk()
    app = AutoReviewTool(root)
    root.mainloop()


def restart_program():
    """Restart the current program."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


def start_watchdog():
    def on_change():
        root.destroy()  # thoát mainloop an toàn
        restart_program()

    observer = Observer()
    event_handler = ReloadHandler(on_change)
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    print("👀 Watchdog started, watching for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # Start watchdog in background thread
    watcher_thread = Thread(target=start_watchdog, daemon=True)
    watcher_thread.start()

    # Start GUI
    launch_gui()

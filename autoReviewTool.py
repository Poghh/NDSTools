import sys
import subprocess
import time
from tkinterdnd2 import TkinterDnD
from tkinter import ttk
from toolsUI.beTab.ui_be import BackEndTab
from toolsUI.ui_fe import FrontEndTab
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if "--watch" in sys.argv:

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self):
            self.process = None
            self.restart_app()

        def restart_app(self):
            if self.process:
                print("🛑 Dừng app cũ...")
                self.process.kill()
                self.process.wait()
            print("🔁 Đang khởi động lại app...")
            self.process = subprocess.Popen(["python", __file__])

        def on_modified(self, event):
            if str(event.src_path).endswith(".py"):
                print(f"📝 File thay đổi: {event.src_path}")
                self.restart_app()

    if __name__ == "__main__":
        print("👀 Watchdog bắt đầu theo dõi thay đổi...")
        observer = Observer()
        handler = ReloadHandler()
        observer.schedule(handler, path=".", recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            if handler.process:
                handler.process.kill()
                handler.process.wait()
        observer.join()

else:
    # === Đây là phần chạy GUI chính ===
    class AutoReviewTool:
        def __init__(self, root):
            self.root = root
            self.root.title("Review Tool")
            self.root.geometry("1200x780")

            self.tab_parent = ttk.Notebook(self.root)
            self.tab_parent.pack(fill="both", expand=True)

            # Tab FE
            self.fe_tab = FrontEndTab(self.tab_parent)

            # Tab BE
            self.be_tab = BackEndTab(self.tab_parent)

    if __name__ == "__main__":
        root = TkinterDnD.Tk()
        app = AutoReviewTool(root)
        root.mainloop()

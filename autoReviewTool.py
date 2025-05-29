from tkinterdnd2 import TkinterDnD
from tkinter import ttk
from toolsUI.beTab.ui_be import BackEndTab
from toolsUI.ui_fe import FrontEndTab


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


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AutoReviewTool(root)
    root.mainloop()

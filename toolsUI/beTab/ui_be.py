import tkinter as tk
from tkinter import scrolledtext, ttk

from .subTabs.comment_and_unit_test_tab import CommentAndUnitTestTab
from .subTabs.dto_and_db_tab import DtoAndDbTab
from .subTabs.self_check_tab import SelfCheckTab

PRIMARY_COLOR = "#2563eb"  # xanh primary
PRIMARY_DARK = "#1d4ed8"
SIDEBAR_BG = "#111827"
TEXT_MUTED = "#6b7280"
APP_BG = "#f3f4f6"


class BackEndTab:
    def __init__(self, parent):
        self.tab = tk.Frame(parent, bg=APP_BG)
        parent.add(self.tab, text="Back-End")

        # style dùng trong build_selfcheck_frame (lookup background)
        self.style = ttk.Style()

        self.build_ui()

    def build_ui(self):
        # Layout chính: sidebar (col 0) + content (col 1)
        self.tab.columnconfigure(0, weight=0)
        self.tab.columnconfigure(1, weight=1)
        self.tab.rowconfigure(0, weight=1)

        # ===================== SIDEBAR BÊN TRÁI =====================
        sidebar = tk.Frame(self.tab, bg=SIDEBAR_BG, width=220)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.rowconfigure(99, weight=1)  # đẩy khoảng trống xuống dưới

        tk.Label(
            sidebar,
            text="Menu",
            bg=SIDEBAR_BG,
            fg="#e5e7eb",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(10, 6), padx=10)

        self.workflow_var = tk.StringVar(value="selfcheck")

        def make_side_btn(text, name):
            return tk.Button(
                sidebar,
                text=text,
                anchor="w",
                bd=0,
                relief="flat",
                bg=SIDEBAR_BG,
                fg="#e5e7eb",
                activebackground=PRIMARY_DARK,
                activeforeground="#ffffff",
                padx=14,
                pady=8,
                font=("Segoe UI", 9),
                highlightthickness=0,
                width=20,
                command=lambda: self.show_workflow(name),
            )

        self.btn_sc = make_side_btn("🧾  Self Check", "selfcheck")
        self.btn_sc.pack(fill="x")

        self.btn_cm = make_side_btn("📝  Comment & Unit Test", "comment")
        self.btn_cm.pack(fill="x")

        self.btn_dev = make_side_btn("🛠  DTO & DB Tools", "devtools")
        self.btn_dev.pack(fill="x")

        # ===================== CONTENT BÊN PHẢI =====================
        main = ttk.Frame(self.tab, style="TFrame")
        main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main.rowconfigure(0, weight=0)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # Card chứa workflow
        container_card = ttk.Frame(main, style="Card.TFrame")
        container_card.grid(row=0, column=0, sticky="ew")
        container_card.columnconfigure(0, weight=1)

        self.workflow_container = ttk.Frame(container_card, style="Card.TFrame")
        self.workflow_container.grid(row=0, column=0, sticky="ew")
        self.workflow_container.columnconfigure(0, weight=1)

        # Card chứa Notebook kết quả
        notebook_card = ttk.Frame(main, style="Card.TFrame")
        notebook_card.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        notebook_card.rowconfigure(0, weight=1)
        notebook_card.columnconfigure(0, weight=1)

        self.output_notebook = ttk.Notebook(notebook_card)
        self.output_notebook.grid(row=0, column=0, sticky="nsew")

        # Tạo 4 tab kết quả
        self.build_output_tabs()

        # === BUILD 3 WORKFLOW FRAMES ===
        self.selfcheck_tab = SelfCheckTab(
            parent=self.workflow_container,
            style=self.style,
        )
        self.comment_and_unit_test_tab = CommentAndUnitTestTab(
            parent=self.workflow_container,
            style=self.style,
        )
        self.dto_and_db_tab = DtoAndDbTab(
            parent=self.workflow_container,
            style=self.style,
        )

        # Ẩn 2 tab còn lại lúc khởi tạo
        self.comment_and_unit_test_tab.frame.grid_remove()
        self.dto_and_db_tab.frame.grid_remove()

        # Mặc định hiển thị Self Check
        self.show_workflow("selfcheck")

    def show_workflow(self, name: str):
        """Hiển thị đúng workflow và cập nhật sidebar."""
        # Ẩn tất cả frame workflow
        for t in (
            self.selfcheck_tab,
            self.comment_and_unit_test_tab,
            self.dto_and_db_tab,
        ):
            t.frame.grid_remove()

        # Hiện đúng frame
        if name == "selfcheck":
            self.selfcheck_tab.frame.grid(row=0, column=0, sticky="nsew")
        elif name == "comment":
            self.comment_and_unit_test_tab.frame.grid(row=0, column=0, sticky="nsew")
        elif name == "devtools":
            self.dto_and_db_tab.frame.grid(row=0, column=0, sticky="nsew")

        self.workflow_var.set(name)
        self._set_sidebar_active(name)

    # ------------------------------------------------------------------ #
    # OUTPUT NOTEBOOK
    # ------------------------------------------------------------------ #
    def build_output_tabs(self):
        # Tab Log
        tab_log = ttk.Frame(self.output_notebook)
        self.output_notebook.add(tab_log, text="Log")

        self.log_text = scrolledtext.ScrolledText(
            tab_log, wrap=tk.WORD, borderwidth=0, background="#ffffff"
        )
        self.log_text.pack(fill="both", expand=True)

        # Tab Self Check Result
        tab_sc = ttk.Frame(self.output_notebook)
        self.output_notebook.add(tab_sc, text="Self Check Result")

        self.sc_result_text = scrolledtext.ScrolledText(
            tab_sc, wrap=tk.WORD, borderwidth=0, background="#ffffff"
        )
        self.sc_result_text.pack(fill="both", expand=True)

        # Tab Comment & UT
        tab_cm = ttk.Frame(self.output_notebook)
        self.output_notebook.add(tab_cm, text="Comment & Unit Test")

        self.cm_result_text = scrolledtext.ScrolledText(
            tab_cm, wrap=tk.WORD, borderwidth=0, background="#ffffff"
        )
        self.cm_result_text.pack(fill="both", expand=True)

        # Tab DTO / DB
        tab_dev = ttk.Frame(self.output_notebook)
        self.output_notebook.add(tab_dev, text="DTO / DB")

        self.dev_result_text = scrolledtext.ScrolledText(
            tab_dev, wrap=tk.WORD, borderwidth=0, background="#ffffff"
        )
        self.dev_result_text.pack(fill="both", expand=True)

    def _set_sidebar_active(self, active_name: str):
        """Đổi màu nút sidebar theo mục đang chọn (chỉ highlight, chưa ẩn/hiện nội dung)."""
        self.workflow_var.set(active_name)

        normal_bg = SIDEBAR_BG
        normal_fg = "#e5e7eb"
        active_bg = PRIMARY_COLOR
        active_fg = "#ffffff"

        buttons = [
            ("selfcheck", self.btn_sc),
            ("comment", self.btn_cm),
            ("devtools", self.btn_dev),
        ]

        for name, btn in buttons:
            if name == active_name:
                btn.configure(bg=active_bg, fg=active_fg, font=("Segoe UI", 9, "bold"))
            else:
                btn.configure(bg=normal_bg, fg=normal_fg, font=("Segoe UI", 9))

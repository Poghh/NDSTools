import tkinter as tk
from tkinter import ttk


class CommentAndUnitTestTab:
    def __init__(self, parent, style, fake_action=None, fake_fill_from_selfcheck=None):
        self.parent = parent
        self.style = style
        self.fake_action = fake_action or (lambda *a, **k: None)
        self.fake_fill_from_selfcheck = fake_fill_from_selfcheck or (lambda: None)

        # 👉 chỉ tạo frame, KHÔNG grid ở đây
        self.frame = ttk.Frame(self.parent, style="Card.TFrame")
        self.frame.columnconfigure(0, weight=1)

        self.build()

    def build(self):
        frame = self.frame

        ttk.Label(frame, text="Comment & Unit Test", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(2, 6), padx=10
        )

        # Tên tác giả
        ttk.Label(frame, text="Tên tác giả:").grid(row=1, column=0, sticky="e", pady=2, padx=10)
        self.author_entry = ttk.Entry(frame, width=30, style="Borderless.TEntry")
        self.author_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Mã màn hình
        ttk.Label(frame, text="Mã màn hình:").grid(row=2, column=0, sticky="e", pady=2, padx=10)

        sc_row = tk.Frame(frame, bd=0, highlightthickness=0)
        sc_row.grid(row=2, column=1, sticky="w")

        self.screen_code_entry = ttk.Entry(sc_row, width=20, style="Borderless.TEntry")
        self.screen_code_entry.pack(side="left")

        ttk.Button(
            sc_row,
            text="Lấy từ Self Check",
            style="Borderless.TButton",
            command=self.fake_fill_from_selfcheck,
        ).pack(side="left", padx=(6, 0))

        # Ngày
        ttk.Label(frame, text="Ngày:").grid(row=3, column=0, sticky="e", pady=2, padx=10)
        self.date_entry = ttk.Entry(frame, width=20, style="Borderless.TEntry")
        self.date_entry.insert(0, "2025/11/13")
        self.date_entry.grid(row=3, column=1, sticky="w", pady=2)

        # Hàng button
        btn_row = tk.Frame(frame, bd=0, highlightthickness=0)
        btn_row.grid(row=4, column=0, columnspan=2, pady=(10, 6), padx=10)

        ttk.Button(
            btn_row,
            text="📝 Tạo Comment",
            style="Borderless.TButton",
            command=lambda: self.fake_action("Tạo Comment", "cm"),
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_row,
            text="🧪 Sinh Unit Test (Dialog)",
            style="Borderless.TButton",
            command=lambda: self.fake_action("Sinh Unit Test (Dialog)", "cm"),
        ).pack(side="left", padx=5)

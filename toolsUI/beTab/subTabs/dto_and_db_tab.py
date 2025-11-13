import tkinter as tk
from tkinter import ttk


class DtoAndDbTab:
    def __init__(self, parent, style, fake_action=None):
        self.parent = parent
        self.style = style
        self.fake_action = fake_action or (lambda *a, **k: None)

        # 👉 chỉ tạo frame, KHÔNG grid ở đây
        self.frame = ttk.Frame(self.parent, style="Card.TFrame")
        self.frame.columnconfigure(0, weight=1)

        self.build()

    def build(self):
        """Workflow 3: DTO & DB Tools"""
        frame = self.frame

        ttk.Label(frame, text="DTO & DB Tools", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(2, 6), padx=10
        )

        # ==== DTO ====
        dto_group = ttk.Labelframe(frame, text="DTO", style="Card.TLabelframe")
        dto_group.grid(row=1, column=0, sticky="ew", pady=(0, 8), padx=10)
        dto_group.columnconfigure(0, weight=1)

        self.dto_file_label = ttk.Label(
            dto_group, text="Chưa chọn file Excel", style="Muted.TLabel"
        )
        self.dto_file_label.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        dto_btn_row = tk.Frame(dto_group, bd=0, highlightthickness=0)
        dto_btn_row.grid(row=1, column=0, sticky="w", pady=(2, 8), padx=8)

        ttk.Button(
            dto_btn_row,
            text="📄 Chọn File Excel",
            style="FlatWhite.TButton",
            command=lambda: self.fake_action("Chọn File Excel", "dev"),
        ).pack(side="left", padx=2)

        ttk.Button(
            dto_btn_row,
            text="⚙ Generate DTO",
            style="FlatWhite.TButton",
            command=lambda: self.fake_action("Generate DTO", "dev"),
        ).pack(side="left", padx=2)

        # ==== Database ====
        db_group = ttk.Labelframe(frame, text="Database", style="Card.TLabelframe")
        db_group.grid(row=2, column=0, sticky="ew", pady=(0, 8), padx=10)
        db_group.columnconfigure(0, weight=1)

        ttk.Button(
            db_group,
            text="🛠 Khởi tạo DB",
            style="Secondary.TButton",
            command=lambda: self.fake_action("Khởi tạo DB", "dev"),
        ).grid(row=0, column=0, sticky="w", pady=4, padx=8)

        ttk.Button(
            db_group,
            text="📂 Tạo Data từ thư mục SQL",
            style="Secondary.TButton",
            command=lambda: self.fake_action("Tạo Data từ thư mục SQL", "dev"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 8), padx=8)

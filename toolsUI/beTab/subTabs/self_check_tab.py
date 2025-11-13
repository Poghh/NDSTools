import tkinter as tk
from tkinter import ttk


class SelfCheckTab:
    def __init__(self, parent, style):
        self.parent = parent
        self.style = style

        self.frame = ttk.Frame(parent, style="Card.TFrame")
        self.frame.columnconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self):
        frame = self.frame

        ttk.Label(frame, text="Self Check", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(2, 6), padx=10
        )
        frame.columnconfigure(0, weight=1)

        # --- Codes group ---
        codes_group = ttk.Labelframe(frame, text="Danh sách mã màn hình", style="Card.TLabelframe")
        codes_group.grid(row=1, column=0, sticky="ew", pady=(0, 8), padx=10)
        codes_group.columnconfigure(0, weight=1)

        ttk.Label(codes_group, text="Dán mã màn hình (GUIxxxxx)", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w", pady=(4, 2), padx=8
        )

        self.codes_text = tk.Text(
            codes_group,
            height=7,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#e5e7eb",
        )
        self.codes_text.grid(row=1, column=0, sticky="ew", padx=(8, 4), pady=(0, 8))

        # — Buttons —
        btns = tk.Frame(codes_group, bg=self.style.lookup("Card.TLabelframe", "background"))
        btns.grid(row=1, column=1, sticky="n", padx=(0, 8), pady=(0, 8))

        ttk.Button(btns, text="Dán\nclipboard", style="Secondary.TButton").pack(
            pady=(0, 4), fill="x"
        )

        ttk.Button(
            btns,
            text="Xoá\nhết",
            style="Secondary.TButton",
            command=lambda: self.codes_text.delete("1.0", tk.END),
        ).pack(fill="x")

        # --- Toolbar ---
        toolbar = ttk.Frame(frame, style="Card.TFrame")
        toolbar.grid(row=2, column=0, sticky="ew", pady=(4, 4), padx=10)

        ttk.Button(
            toolbar,
            text="📂 Chọn thư mục",
            style="Secondary.TButton",
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            toolbar,
            text="📄 Tải File",
            style="Secondary.TButton",
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            toolbar,
            text="📊 Đếm dòng code",
            style="Primary.TButton",
        ).grid(row=0, column=2, padx=4)

        ttk.Button(
            toolbar,
            text="🧾 Xuất báo cáo",
            style="Primary.TButton",
        ).grid(row=0, column=3, padx=4)

        self.frame = frame

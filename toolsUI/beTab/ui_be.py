import tkinter as tk
from tkinter import scrolledtext
from tkcalendar import DateEntry
from toolsUI.beTab.unit_test_generater_dialog import UnitTestDialog
from toolsAction.beActions.select_file import select_file
from toolsAction.beActions.comment_generator import generate_comment
from toolsAction.beActions.create_java_dto_class import generated_dto
from tkinter import scrolledtext


class BackEndTab:
    def __init__(self, parent):
        self.tab = tk.Frame(parent)
        parent.add(self.tab, text="Back-End")
        self.build_ui()

    def build_ui(self):
        # === Layout: Input bên trái, Output bên phải ===
        frame_input = tk.Frame(self.tab, width=240, bg="lightgray")
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        frame_output = tk.Frame(self.tab)
        frame_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # === FILE SELECT & DTO ===
        self.file_path = None  # <-- thêm biến lưu đường dẫn file
        self.file_path_label = tk.Label(
            frame_input, text="Chưa chọn file", bg="lightgray", width=30
        )
        self.file_path_label.pack(pady=10)

        tk.Button(
            frame_input, text="Chọn File Excel", command=lambda: select_file(self)
        ).pack(pady=5)
        tk.Button(
            frame_input, text="Generate DTO", command=lambda: generated_dto(self)
        ).pack(pady=5)

        # === COMMENT GENERATOR ===
        tk.Label(frame_input, text="-------------------------", bg="lightgray").pack(
            pady=10
        )

        tk.Label(
            frame_input,
            text="Tạo Comment File",
            bg="lightgray",
            font=("Arial", 10, "bold"),
        ).pack(pady=5)

        tk.Label(frame_input, text="Tên tác giả:", bg="lightgray").pack()
        self.author_entry = tk.Entry(frame_input, width=25)
        self.author_entry.pack(pady=2)

        tk.Label(frame_input, text="Mã màn hình:", bg="lightgray").pack()
        self.screen_code_entry = tk.Entry(frame_input, width=25)
        self.screen_code_entry.pack(pady=2)

        tk.Label(frame_input, text="Chọn ngày:", bg="lightgray").pack()
        self.date_entry = DateEntry(
            frame_input,
            width=22,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy/mm/dd",
        )
        self.date_entry.pack(pady=2)

        tk.Button(
            frame_input, text="Tạo Comment", command=lambda: generate_comment(self)
        ).pack(pady=10)

        # # === Sinh Unit Test (Dialog) ===
        tk.Button(
            frame_input,
            text="Sinh Unit Test (Dialog)",
            command=lambda: UnitTestDialog(self.tab),
        ).pack(pady=10)

        # === OUTPUT TEXT ===
        self.output_text = scrolledtext.ScrolledText(
            frame_output, wrap=tk.WORD, width=80, height=30
        )
        self.output_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

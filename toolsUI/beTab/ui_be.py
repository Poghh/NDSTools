import tkinter as tk
from tkinter import messagebox, scrolledtext

from tkcalendar import DateEntry

from toolsAction.beActions.comment_generator import generate_comment
from toolsAction.beActions.count_code import count_code
from toolsAction.beActions.create_java_dto_class import generated_dto
from toolsAction.beActions.process_selfcheck_excel import select_self_check_file
from toolsAction.beActions.run_database_initialization import (
    run_database_initialization,
)
from toolsAction.beActions.run_sql_folder import run_sql_from_folder
from toolsAction.beActions.select_file import select_file
from toolsUI.beTab.unit_test_generater_dialog import UnitTestDialog


class BackEndTab:
    def __init__(self, parent):
        self.tab = tk.Frame(parent)
        parent.add(self.tab, text="Back-End")
        self.build_ui()

    def build_ui(self):
        # === Cấu hình bố cục chính cho self.tab ===
        self.tab.columnconfigure(0, weight=1)
        self.tab.columnconfigure(1, weight=3)
        self.tab.rowconfigure(0, weight=1)

        # === FRAME TRÁI ===
        frame_input = tk.Frame(self.tab, bg="lightgray")
        frame_input.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        frame_input.columnconfigure(0, weight=1)

        # === FRAME PHẢI ===
        frame_output = tk.Frame(self.tab)
        frame_output.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame_output.rowconfigure(0, weight=1)
        frame_output.columnconfigure(0, weight=1)

        # === [1] SELF CHECK === (được đưa lên đầu tiên)
        helper_frame = tk.LabelFrame(frame_input, text=" Self Check", bg="lightgray")
        helper_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.self_check_path = None
        self.self_check_label = tk.Label(
            helper_frame, text="Chưa chọn file", bg="lightgray", font=("Arial", 8)
        )
        self.self_check_label.pack(pady=(2, 0), anchor="center")

        tk.Button(
            helper_frame,
            text="Tải File Self Check",
            command=lambda: select_self_check_file(self),
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Button(
            helper_frame,
            text="Đếm dòng code từ Self Check",
            command=lambda: count_code(self.file_listbox, self.output_text),
        ).pack(pady=2, anchor="center")

        tk.Label(
            helper_frame,
            text="Danh sách file đã load:",
            bg="lightgray",
            font=("Arial", 8),
        ).pack(anchor="w", padx=5, pady=(5, 0))

        listbox_frame = tk.Frame(helper_frame)
        listbox_frame.pack(padx=5, pady=2, fill=tk.BOTH, expand=True)

        x_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.file_listbox = tk.Listbox(listbox_frame, height=6, xscrollcommand=x_scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        x_scrollbar.config(command=self.file_listbox.xview)

        # === [2] COMMENT & UNIT TEST GENERATOR ===
        comment_frame = tk.LabelFrame(
            frame_input, text="Tạo Comment cho File & Unit Test", bg="lightgray"
        )
        comment_frame.grid(row=1, column=0, sticky="ew", pady=10)

        tk.Label(comment_frame, text="Tên tác giả:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.author_entry = tk.Entry(comment_frame, width=25)
        self.author_entry.pack(pady=2, anchor="center")

        tk.Label(comment_frame, text="Mã màn hình:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.screen_code_entry = tk.Entry(comment_frame, width=25)
        self.screen_code_entry.pack(pady=2, anchor="center")

        tk.Label(comment_frame, text="Chọn ngày:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.date_entry = DateEntry(
            comment_frame,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy/mm/dd",
            width=22,
        )
        self.date_entry.pack(pady=2, anchor="center")

        tk.Button(
            comment_frame,
            text="Tạo Comment",
            command=lambda: generate_comment(self),
            width=25,
        ).pack(pady=(5, 2), anchor="center")

        tk.Button(
            comment_frame,
            text="Sinh Unit Test (Dialog)",
            command=self.check_and_open_unittest_dialog,
            width=25,
        ).pack(pady=(0, 5), anchor="center")

        # === [3] FILE CHỌN & DTO === (di chuyển xuống cuối)
        file_frame = tk.LabelFrame(frame_input, text="Chọn File & Tạo DTO", bg="lightgray")
        file_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.file_path = None
        self.file_path_label = tk.Label(file_frame, text="Chưa chọn file", bg="lightgray")
        self.file_path_label.pack(pady=5, anchor="center")

        tk.Button(
            file_frame,
            text="Chọn File Excel",
            command=lambda: select_file(self),
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Button(
            file_frame,
            text="Generate DTO",
            command=lambda: generated_dto(self),
            width=25,
        ).pack(pady=2, anchor="center")

        # === [4] NÚT KHỞI TẠO DB ===
        init_db_frame = tk.LabelFrame(frame_input, text="Khởi tạo Cơ sở dữ liệu", bg="lightgray")
        init_db_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        tk.Button(
            init_db_frame,
            text="Khởi tạo DB",
            command=lambda: run_database_initialization(self),
            width=25,
        ).pack(pady=5, anchor="center")

        tk.Button(
            init_db_frame,
            text="Tạo Data từ thư mục SQL",
            command=lambda: run_sql_from_folder(self),
            width=25,
        ).pack(pady=(0, 5), anchor="center")

        # === OUTPUT TEXT ===
        self.output_text = scrolledtext.ScrolledText(frame_output, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew")

    def check_and_open_unittest_dialog(self):
        screen_code = self.screen_code_entry.get().strip()

        if not screen_code:
            messagebox.showwarning(
                "Thiếu thông tin", "Vui lòng nhập đầy đủ Tên tác giả và Mã màn hình."
            )
            return

        UnitTestDialog(self.tab, screen_code=screen_code)

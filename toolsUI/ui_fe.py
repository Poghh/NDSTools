import tkinter as tk
from tkinter import scrolledtext, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import pandas as pd
from tkinter import scrolledtext, filedialog
import threading
from toolsAction.feActions.eslint_tool import run_eslint
from toolsAction.feActions.line_counter import count_lines
from toolsAction.feActions.title_checker import check_title_comment
from toolsAction.feActions.css_checker import check_css_color_main
from toolsAction.feActions.hardcode_checker import check_hardcode_jp
from toolsAction.feActions.console_checker import check_console_log
from toolsAction.feActions.jsdoc_checker import check_jsdoc
from toolsAction.feActions.vue_order_checker import check_vue_order_main
from toolsAction.feActions.english_comment_checker import check_english_comments_main
from toolsAction.feActions.hardcode_value_checker import check_hardcoded_values_main


class FrontEndTab:
    def __init__(self, tab_parent):
        self.tab = ttk.Frame(tab_parent)
        tab_parent.add(self.tab, text="🌐 Front-End")

        self.init_ui()

    def init_ui(self):
        self.root = self.tab  # để tái sử dụng layout gốc

        self.root.title = lambda title: None
        self.root.geometry = lambda geom: None

        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill='x', padx=10, pady=(10, 5))

        self.frame_input = tk.LabelFrame(
            self.top_frame, text="🔹 Nhập danh sách path cần kiểm tra", padx=10, pady=10)
        self.frame_input.pack(side=tk.LEFT, fill='both',
                              expand=True, padx=(0, 5))

        self.selfcheck_frame = tk.Frame(self.frame_input)
        self.selfcheck_frame.pack(fill='x', pady=(0, 5))

        self.upload_selfcheck_btn = tk.Button(
            self.selfcheck_frame, text="📂 Tải file Self-check", command=self.upload_selfcheck)
        self.upload_selfcheck_btn.pack(side=tk.LEFT)

        self.selfcheck_label = tk.Label(
            self.selfcheck_frame, text="Chưa chọn file", fg="gray")
        self.selfcheck_label.pack(side=tk.LEFT, padx=(10, 0))

        self.path_input = scrolledtext.ScrolledText(
            self.frame_input, height=10, wrap=tk.WORD, font=("Consolas", 10))
        self.path_input.pack(fill='both', expand=True)

        self.path_input.drop_target_register(DND_FILES)
        self.path_input.dnd_bind('<<Drop>>', self.handle_drop)

        self.frame_future = tk.LabelFrame(
            self.top_frame, text="🧩 Tải lên tài liệu (Excel)", padx=10, pady=10)
        self.frame_future.pack(side=tk.LEFT, fill='both',
                               expand=True, padx=(5, 0))

        self.upload_excel_btn = tk.Button(
            self.frame_future, text="📂 Tải file tài liệu", command=self.upload_excel_docs)
        self.upload_excel_btn.pack(anchor='nw')

        self.excel_label = tk.Label(
            self.frame_future, text="Chưa chọn file", fg="gray")
        self.excel_label.pack(anchor='nw', pady=(5, 5))

        self.excel_output = scrolledtext.ScrolledText(
            self.frame_future, height=6, wrap=tk.WORD, font=("Consolas", 10))
        self.excel_output.pack(fill='both', expand=True)

        self.excel_output.drop_target_register(DND_FILES)
        self.excel_output.dnd_bind('<<Drop>>', self.handle_docs_drop)

        self.author_subframe = tk.Frame(self.frame_future)
        self.author_subframe.pack(fill='x', pady=(10, 0))

        tk.Label(self.author_subframe, text="👤 Nhập tên tác giả:").pack(
            side=tk.LEFT, padx=(0, 10))
        self.author_var = tk.StringVar()
        self.author_var.trace_add("write", self.convert_author_to_uppercase)
        self.author_entry = tk.Entry(
            self.author_subframe, textvariable=self.author_var)
        self.author_entry.pack(side=tk.LEFT, fill='x', expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=(0, 10))

        btn_width = 20


        # row 0
        self.run_button = tk.Button(
            btn_frame, text="🚀 Run ESLint", width=btn_width, command=self.on_run_eslint)
        self.run_button.grid(row=0, column=0, padx=10, pady=5)

        self.check_title_button = tk.Button(
            btn_frame, text="📝 Check Title", width=btn_width, command=self.on_check_title_comment)
        self.check_title_button.grid(row=0, column=1, padx=10, pady=5)

        self.check_color_button = tk.Button(
            btn_frame, text="🎨 Check CSS", width=btn_width, command=self.on_check_css_color)
        self.check_color_button.grid(row=0, column=2, padx=10, pady=5)

        self.check_hardcode_button = tk.Button(
            btn_frame, text="🔍 Check JP Text", width=btn_width, command=self.on_check_hardcode_jp)
        self.check_hardcode_button.grid(row=0, column=3, padx=10, pady=5)

        self.check_console_button = tk.Button(
            btn_frame, text="🛑 Check Console", width=btn_width, command=self.on_check_console)
        self.check_console_button.grid(row=0, column=4, padx=10, pady=5)

        # row 1
        self.check_english_comments_button = tk.Button(
            btn_frame, text="🔤 Check Eng Cmt", width=btn_width, command=self.on_check_english_comments)
        self.check_english_comments_button.grid(
            row=1, column=0, padx=10, pady=5)

        self.check_hardcode_values_button = tk.Button(
            btn_frame, text="🔒 Check Values", width=btn_width, command=self.on_check_hardcode_values)
        self.check_hardcode_values_button.grid(
            row=1, column=1, padx=10, pady=5)

        self.count_button = tk.Button(
            btn_frame, text="🧮 Count Lines", width=btn_width, command=self.on_count_lines)
        self.count_button.grid(row=1, column=2, padx=10, pady=5)

        # row 2
        self.check_jsdoc_button = tk.Button(
            btn_frame, text="📘 Check JSDoc", width=btn_width, command=self.on_check_jsdoc)
        self.check_jsdoc_button.grid(row=2, column=0, padx=10, pady=5)

        self.check_vue_order_button = tk.Button(
            btn_frame, text="⚡ Check Vue", width=btn_width, command=self.on_check_vue_order)
        self.check_vue_order_button.grid(row=2, column=1, padx=10, pady=5)

        self.clear_button = tk.Button(
            btn_frame, text="🔄 Clear All", width=btn_width, command=self.clear_all)
        self.clear_button.grid(row=2, column=2, padx=10, pady=5)
        
        self.status_label = tk.Label(
            self.root, text="", fg="blue", font=("Segoe UI", 12, "italic"))
        self.status_label.pack(pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(expand=True, fill='both', padx=10, pady=10)

        self.output_text.tag_configure(
            "error", foreground="red", font=("Consolas", 12, "bold"))
        self.output_text.tag_configure(
            "highlight", foreground="blue", font=("Consolas", 12, "italic"))
        self.output_text.tag_configure(
            "warning", foreground="#FF6600", font=("Consolas", 12, "italic"))
        self.output_text.tag_configure(
            "success", foreground="green", font=("Consolas", 12, "italic"))
        self.output_text.tag_configure(
            "title-color", foreground="blue", font=("Consolas", 12, "bold"))
        self.output_text.tag_configure(
            "footer-color", foreground="gray", font=("Consolas", 12, "bold"))

    def handle_drop(self, event):
        try:
            file_path = event.data
            # Convert TK DND path format to normal path
            if file_path.startswith('{'):
                file_path = file_path[1:-1]

            # Check if it's an Excel file
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                self.selfcheck_label.config(
                    text="❌ Chỉ chấp nhận file Excel", fg="red")
                return

            # Process the Excel file
            self.process_selfcheck_excel(file_path)
        except Exception as e:
            self.selfcheck_label.config(text=f"❌ Lỗi: {str(e)}", fg="red")

    def process_selfcheck_excel(self, file_path):
        if not file_path:
            self.selfcheck_label.config(
                text="❌ Không có file nào được chọn", fg="red")
            self.path_input.delete("1.0", tk.END)
            return

        file_name = os.path.basename(file_path)
        self.selfcheck_label.config(text=f"📁 {file_name}", fg="green")
        self.path_input.delete("1.0", tk.END)

        try:
            workbook = pd.read_excel(
                file_path, sheet_name='機能別ソース一覧', header=None)
        except Exception as e:
            self.path_input.insert(
                tk.END, f"❌ Lỗi khi đọc sheet 機能別ソース一覧: {str(e)}\n")
            return

        result = []
        for index, row in workbook.iterrows():
            if row[3] == "新規":
                result.append(row[2])

        for item in result:
            self.path_input.insert(tk.END, f"{item}\n")

    def handle_docs_drop(self, event):
        try:
            file_path = event.data
            # Convert TK DND path format to normal path
            if file_path.startswith('{'):
                file_path = file_path[1:-1]

            # Check if it's an Excel file
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                self.excel_label.config(
                    text="❌ Chỉ chấp nhận file Excel", fg="red")
                return

            # Process the Excel file
            self.process_excel_docs(file_path)
        except Exception as e:
            self.excel_label.config(text=f"❌ Lỗi: {str(e)}", fg="red")

    def process_excel_docs(self, file_path):
        if not file_path:
            self.excel_label.config(
                text="❌ Không có file nào được chọn", fg="red")
            self.excel_output.delete("1.0", tk.END)
            return

        file_name = os.path.basename(file_path)
        self.excel_label.config(text=f"📁 {file_name}", fg="green")
        self.excel_output.delete("1.0", tk.END)

        try:
            workbook = pd.read_excel(file_path, sheet_name='項目一覧', header=None)
        except Exception as e:
            self.excel_output.insert(
                tk.END, f"❌ Lỗi khi đọc sheet 項目一覧: {str(e)}\n")
            return

        result = []
        mark_gui = None

        # Tìm cột chứa "画面No."
        for col_idx, cell in enumerate(workbook.iloc[0]):
            if str(cell).strip() == "画面No." or str(cell).strip() == "画面No．" or "画面No" in str(cell).strip():
                mark_gui = col_idx
                break

        for _, row in workbook.iterrows():
            if len(row) > mark_gui+1:
                code = row[mark_gui+1]
                name = row[mark_gui+1+1] if len(row) > mark_gui+1+1 else ''
                if pd.notna(code) and isinstance(code, str) and 'Or' in code:
                    result.append(
                        {'code': code.strip(), 'name': str(name).strip()})

        seen = set()
        unique_result = []
        if mark_gui is not None:
            try:
                item_gui = {
                    'code': str(workbook.iloc[0, mark_gui + 1]).strip(),
                    'name': str(workbook.iloc[1, mark_gui + 1]).strip()
                }
                unique_result.append(item_gui)
            except Exception as e:
                self.excel_output.insert(
                    tk.END, f"⚠️ Lỗi khi lấy GUI code/name: {str(e)}\n")

        for item in result:
            if item['code'] not in seen:
                seen.add(item['code'])
                unique_result.append(item)

        for item in unique_result:
            self.excel_output.insert(
                tk.END, f"🔹 {item['code']} - {item['name']}\n")

    def upload_selfcheck(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file Self-check Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        self.process_selfcheck_excel(file_path)

    def upload_excel_docs(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel tài liệu",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        self.process_excel_docs(file_path)

    def convert_author_to_uppercase(self, *args):
        current = self.author_var.get()
        upper = current.upper()
        if current != upper:
            self.author_var.set(upper)

    def on_run_eslint(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=run_eslint, args=(self,)).start()

    def on_count_lines(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=count_lines, args=(self,)).start()

    def on_check_title_comment(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_title_comment, args=(self,)).start()

    def on_check_css_color(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_css_color_main, args=(self,)).start()

    def on_check_hardcode_jp(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_hardcode_jp, args=(self,)).start()

    def on_check_console(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_console_log, args=(self,)).start()

    def on_check_jsdoc(self):
        # threading.Thread(target=check_jsdoc, args=(self,)).start()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert('end', '📘 Tính năng tạm ngừng\n', 'warning')

    def on_check_vue_order(self):
        # threading.Thread(target=check_vue_order_main, args=(self,)).start()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert('end', '⚡ Tính năng tạm ngừng\n', 'warning')

    def on_check_english_comments(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_english_comments_main,
                         args=(self,)).start()

    def on_check_hardcode_values(self):
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=check_hardcoded_values_main,
                         args=(self,)).start()

    def get_file_list(self):
        self.output_text.delete("1.0", tk.END)
        input_text = self.path_input.get("1.0", tk.END)
        files = [line.strip()
                 for line in input_text.splitlines() if line.strip()]
        if not files:
            self.output_text.insert(
                tk.END, "❌ Vui lòng nhập danh sách file.\n", "error")
        return files

    def display_output(self, text):
        for line in text.splitlines():
            tag = "error" if any(keyword in line.lower()
                                 for keyword in ["error", "✖", "❌"]) else None
            self.output_text.insert(tk.END, line + "\n", tag)

    def clear_all(self):
        self.path_input.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.status_label.config(text="")
        self.excel_label.config(text="Chưa chọn file", fg="gray")
        self.excel_output.delete("1.0", tk.END)
        self.author_entry.delete(0, tk.END)
        self.selfcheck_label.config(text="Chưa chọn file", fg="gray")

    def set_running_state(self, running: bool):
        state = tk.DISABLED if running else tk.NORMAL
        self.run_button.config(state=state)
        self.count_button.config(state=state)
        self.clear_button.config(state=state)
        self.upload_excel_btn.config(state=state)
        self.upload_selfcheck_btn.config(state=state)
        self.check_title_button.config(state=state)
        self.check_color_button.config(state=state)
        self.check_hardcode_button.config(state=state)
        self.check_console_button.config(state=state)
        self.check_jsdoc_button.config(state=state)
        self.check_vue_order_button.config(state=state)
        self.check_english_comments_button.config(state=state)
        self.check_hardcode_values_button.config(state=state)
        self.status_label.config(
            text="⏳ Đang xử lý..." if running else "✅ Sẵn sàng.")

import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

import pandas as pd
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from toolsAction.feActions.console_checker import check_console_log
from toolsAction.feActions.css_checker import check_css_color_main
from toolsAction.feActions.english_comment_checker import check_english_comments_main
from toolsAction.feActions.eslint_tool import run_eslint
from toolsAction.feActions.hardcode_checker import check_hardcode_jp
from toolsAction.feActions.hardcode_value_checker import check_hardcoded_values_main
from toolsAction.feActions.line_counter import count_lines
from toolsAction.feActions.title_checker import check_title_comment


class FrontEndTab:
    def __init__(self, tab_parent):
        self.tab = ttk.Frame(tab_parent, style="Custom.TFrame")
        tab_parent.add(self.tab, text="Front-End")
        self.icons = {}
        self.eslint_running = False
        self.eslint_thread = None
        # Store icon references to prevent garbage collection
        self.icon_references = []
        self.init_ui()

    def load_icon(self, name, size=(24, 24)):
        path = os.path.join(os.path.dirname(__file__), "assets", name)
        if os.path.exists(path):
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def init_ui(self):
        style = ttk.Style()
        style.configure("Custom.TFrame", background="#f5f7fa")
        style.configure("Custom.TLabelframe", background="#e3eafc", borderwidth=2, relief="ridge")
        style.configure(
            "Custom.TButton",
            font=("Segoe UI", 10),
            padding=6,
            background="#fff",
            foreground="#222",
            borderwidth=1,
            relief="ridge",
        )
        style.map(
            "Custom.TButton",
            background=[("active", "#e3eafc"), ("disabled", "#f0f0f0")],
            foreground=[("active", "#0d47a1"), ("disabled", "#888")],
            bordercolor=[("active", "#2d5be3"), ("!active", "#b0c4de")],
        )
        style.configure("Custom.TLabel", background="#f5f7fa", font=("Segoe UI", 10))
        style.configure(
            "Custom.TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            foreground="#2d5be3",
        )

        self.root = self.tab

        self.top_frame = tk.Frame(self.root, bg="#f5f7fa")
        self.top_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.frame_input = ttk.LabelFrame(
            self.top_frame,
            text=" Nhập danh sách path cần kiểm tra",
            padding=12,
            style="Custom.TLabelframe",
        )
        self.frame_input.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 8))

        self.selfcheck_frame = tk.Frame(self.frame_input, bg="#e3eafc")
        self.selfcheck_frame.pack(fill="x", pady=(0, 8))

        upload_icon = self.load_icon("upload.png")
        # Create button with or without icon
        if upload_icon:
            self.upload_selfcheck_btn = tk.Button(
                self.selfcheck_frame,
                text=" Tải file Self-check",
                image=upload_icon,
                compound=tk.LEFT,
                command=self.upload_selfcheck,
                bg="#fff",
                fg="#222",
                font=("Segoe UI", 10, "bold"),
                relief=tk.RIDGE,
                bd=1,
                activebackground="#e3eafc",
                activeforeground="#0d47a1",
            )
            # Keep reference to prevent garbage collection
            self.icon_references.append(upload_icon)
        else:
            self.upload_selfcheck_btn = tk.Button(
                self.selfcheck_frame,
                text=" Tải file Self-check",
                command=self.upload_selfcheck,
                bg="#fff",
                fg="#222",
                font=("Segoe UI", 10, "bold"),
                relief=tk.RIDGE,
                bd=1,
                activebackground="#e3eafc",
                activeforeground="#0d47a1",
            )
        self.upload_selfcheck_btn.pack(side=tk.LEFT)

        self.selfcheck_label = tk.Label(
            self.selfcheck_frame,
            text="Chưa chọn file",
            fg="gray",
            bg="#e3eafc",
            font=("Segoe UI", 10, "italic"),
        )
        self.selfcheck_label.pack(side=tk.LEFT, padx=(10, 0))

        self.path_input = scrolledtext.ScrolledText(
            self.frame_input,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.path_input.pack(fill="both", expand=True)

        # Enable drag and drop functionality
        try:
            # Use getattr to safely check for drag-and-drop methods
            drop_register = getattr(self.path_input, 'drop_target_register', None)
            dnd_bind = getattr(self.path_input, 'dnd_bind', None)
            if drop_register and dnd_bind:
                drop_register(DND_FILES)
                dnd_bind("<<Drop>>", self.handle_drop)
        except (AttributeError, Exception):
            # If drag and drop is not available, continue without it
            pass

        self.frame_future = ttk.LabelFrame(
            self.top_frame,
            text=" Tải lên tài liệu (Excel)",
            padding=12,
            style="Custom.TLabelframe",
        )
        self.frame_future.pack(side=tk.LEFT, fill="both", expand=True, padx=(8, 0))

        upload_excel_icon = self.load_icon("excel.png")
        # Create button with or without icon
        if upload_excel_icon:
            self.upload_excel_btn = tk.Button(
                self.frame_future,
                text=" Tải file tài liệu",
                image=upload_excel_icon,
                compound=tk.LEFT,
                command=self.upload_excel_docs,
                bg="#fff",
                fg="#222",
                font=("Segoe UI", 10, "bold"),
                relief=tk.RIDGE,
                bd=1,
                activebackground="#e3eafc",
                activeforeground="#0d47a1",
            )
            # Keep reference to prevent garbage collection
            self.icon_references.append(upload_excel_icon)
        else:
            self.upload_excel_btn = tk.Button(
                self.frame_future,
                text=" Tải file tài liệu",
                command=self.upload_excel_docs,
                bg="#fff",
                fg="#222",
                font=("Segoe UI", 10, "bold"),
                relief=tk.RIDGE,
                bd=1,
                activebackground="#e3eafc",
                activeforeground="#0d47a1",
            )
        self.upload_excel_btn.pack(anchor="nw")

        self.excel_label = tk.Label(
            self.frame_future,
            text="Chưa chọn file",
            fg="gray",
            bg="#e3eafc",
            font=("Segoe UI", 10, "italic"),
        )
        self.excel_label.pack(anchor="nw", pady=(5, 5))

        self.excel_output = scrolledtext.ScrolledText(
            self.frame_future,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.excel_output.pack(fill="both", expand=True)

        # Enable drag and drop functionality
        try:
            # Use getattr to safely check for drag-and-drop methods
            drop_register = getattr(self.excel_output, 'drop_target_register', None)
            dnd_bind = getattr(self.excel_output, 'dnd_bind', None)
            if drop_register and dnd_bind:
                drop_register(DND_FILES)
                dnd_bind("<<Drop>>", self.handle_docs_drop)
        except (AttributeError, Exception):
            # If drag and drop is not available, continue without it
            pass

        self.author_subframe = tk.Frame(self.frame_future, bg="#e3eafc")
        self.author_subframe.pack(fill="x", pady=(10, 0))

        tk.Label(
            self.author_subframe,
            text=" Nhập tên tác giả:",
            bg="#e3eafc",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 10))
        self.author_var = tk.StringVar()
        self.author_var.trace_add("write", self.convert_author_to_uppercase)
        self.author_entry = tk.Entry(
            self.author_subframe,
            textvariable=self.author_var,
            font=("Consolas", 10),
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.author_entry.pack(side=tk.LEFT, fill="x", expand=True)

        btn_frame = tk.Frame(self.root, bg="#f5f7fa")
        btn_frame.pack(pady=(0, 16))

        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=200)
        self.progress.pack(pady=(0, 5))
        self.progress.pack_forget()

        # Sắp xếp lại các nút, mỗi hàng 6 nút, tăng bo góc và padding
        btns = [
            (" Run ESLint", self.on_run_eslint),
            (" Check Title", self.on_check_title_comment),
            (" Check CSS", self.on_check_css_color),
            (" Check JP Text", self.on_check_hardcode_jp),
            (" Check Console", self.on_check_console),
            (" Check Eng Cmt", self.on_check_english_comments),
            (" Check Values", self.on_check_hardcode_values),
            (" Count Lines", self.on_count_lines),
            (" Check JSDoc", self.on_check_jsdoc, True),
            (" Check Vue", self.on_check_vue_order, True),
            (" Clear All", self.clear_all),
        ]
        self.buttons = []
        col_count = 6
        for idx, btn in enumerate(btns):
            row = idx // col_count
            col = idx % col_count
            text, cmd = btn[0], btn[1]
            is_disabled = len(btn) > 2 and btn[2]
            b = tk.Button(
                btn_frame,
                text=text,
                width=18,
                command=cmd,
                bg="#fff",
                fg="#222",
                font=("Segoe UI", 10),
                relief=tk.RIDGE,
                bd=2,
                activebackground="#e3eafc",
                activeforeground="#0d47a1",
                highlightthickness=1,
                highlightbackground="#b0c4de",
                padx=8,
                pady=8,
                disabledforeground="#888",
            )
            if is_disabled:
                b.config(state=tk.DISABLED, bg="#f0f0f0", fg="#888")
            b.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.buttons.append(b)
        # Đảm bảo các cột đều nhau
        for i in range(col_count):
            btn_frame.grid_columnconfigure(i, weight=1)

        self.status_label = tk.Label(
            self.root,
            text="",
            fg="#2d5be3",
            bg="#f5f7fa",
            font=("Segoe UI", 12, "italic"),
        )
        self.status_label.pack(pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.output_text.pack(expand=True, fill="both", padx=16, pady=16)

        self.output_text.tag_configure("error", foreground="red", font=("Consolas", 12, "bold"))
        self.output_text.tag_configure(
            "highlight", foreground="blue", font=("Consolas", 12, "italic")
        )
        self.output_text.tag_configure(
            "warning", foreground="#FF6600", font=("Consolas", 12, "italic")
        )
        self.output_text.tag_configure(
            "success", foreground="green", font=("Consolas", 12, "italic")
        )
        self.output_text.tag_configure(
            "title-color", foreground="blue", font=("Consolas", 12, "bold")
        )
        self.output_text.tag_configure(
            "footer-color", foreground="gray", font=("Consolas", 12, "bold")
        )

    def handle_drop(self, event):
        try:
            file_path = event.data
            if file_path.startswith("{"):
                file_path = file_path[1:-1]

            if not file_path.lower().endswith((".xlsx", ".xls")):
                self.selfcheck_label.config(text=" Chỉ chấp nhận file Excel", fg="red")
                return

            self.process_selfcheck_excel(file_path)
        except Exception as e:
            self.selfcheck_label.config(text=f" Lỗi: {str(e)}", fg="red")

    def process_selfcheck_excel(self, file_path):
        if not file_path:
            self.selfcheck_label.config(text=" Không có file nào được chọn", fg="red")
            self.path_input.delete("1.0", tk.END)
            return

        file_name = os.path.basename(file_path)
        self.selfcheck_label.config(text=f" {file_name}", fg="green")
        self.path_input.delete("1.0", tk.END)

        try:
            workbook = pd.read_excel(file_path, sheet_name="機能別ソース一覧", header=None)
        except Exception as e:
            self.path_input.insert(tk.END, f" Lỗi khi đọc sheet 機能別ソース一覧: {str(e)}\n")
            return

        result = []
        name = ""
        for _index, row in workbook.iterrows():
            # Fix pandas Series boolean evaluation
            if pd.notna(row.iloc[4]) and "KMD" in str(row.iloc[4]) and not name:
                full_name = str(row.iloc[4]).strip()
                if "KMD" in full_name:
                    name = full_name.split("KMD", 1)[-1].strip()
                    self.author_var.set(name)
            if row.iloc[3] == "新規":
                result.append(row.iloc[2])

        for item in result:
            self.path_input.insert(tk.END, f"{item}\n")

    def handle_docs_drop(self, event):
        try:
            file_path = event.data
            if file_path.startswith("{"):
                file_path = file_path[1:-1]

            if not file_path.lower().endswith((".xlsx", ".xls")):
                self.excel_label.config(text=" Chỉ chấp nhận file Excel", fg="red")
                return

            self.process_excel_docs(file_path)
        except Exception as e:
            self.excel_label.config(text=f" Lỗi: {str(e)}", fg="red")

    def process_excel_docs(self, file_path):
        if not file_path:
            self.excel_label.config(text=" Không có file nào được chọn", fg="red")
            self.excel_output.delete("1.0", tk.END)
            return

        file_name = os.path.basename(file_path)
        self.excel_label.config(text=f" {file_name}", fg="green")
        self.excel_output.delete("1.0", tk.END)

        try:
            workbook = pd.read_excel(file_path, sheet_name="項目一覧", header=None)
        except Exception as e:
            self.excel_output.insert(tk.END, f" Lỗi khi đọc sheet 項目一覧: {str(e)}\n")
            return

        result = []
        mark_gui = None

        for col_idx, cell in enumerate(workbook.iloc[0]):
            if (
                str(cell).strip() == "画面No."
                or str(cell).strip() == "画面No．"
                or "画面No" in str(cell).strip()
            ):
                mark_gui = col_idx
                break

        for _, row in workbook.iterrows():
            if mark_gui is not None and len(row) > mark_gui + 1:
                code = row.iloc[mark_gui + 1]
                name = row.iloc[mark_gui + 1 + 1] if len(row) > mark_gui + 1 + 1 else ""
                # Fix pandas Series boolean evaluation
                if pd.notna(code) and isinstance(code, str) and "Or" in code:
                    result.append({"code": code.strip(), "name": str(name).strip()})

        seen = set()
        unique_result = []
        if mark_gui is not None:
            try:
                item_gui = {
                    "code": str(workbook.iloc[0, mark_gui + 1]).strip(),
                    "name": str(workbook.iloc[1, mark_gui + 1]).strip(),
                }
                unique_result.append(item_gui)
            except Exception as e:
                self.excel_output.insert(tk.END, f" Lỗi khi lấy GUI code/name: {str(e)}\n")

        for item in result:
            if item["code"] not in seen:
                seen.add(item["code"])
                unique_result.append(item)

        for item in unique_result:
            self.excel_output.insert(tk.END, f" {item['code']} - {item['name']}\n")

    def upload_selfcheck(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file Self-check Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )
        self.process_selfcheck_excel(file_path)

    def upload_excel_docs(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel tài liệu",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )
        self.process_excel_docs(file_path)

    def convert_author_to_uppercase(self, *args):
        current = self.author_var.get()
        upper = current.upper()
        if current != upper:
            self.author_var.set(upper)

    def start_loading(self):
        self.progress.pack(pady=(0, 5))
        self.progress.start(10)
        self.set_running_state(True)

    def stop_loading(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.eslint_running = False
        self.update_eslint_button()
        self.set_running_state(False)

    def on_run_eslint(self):
        self.output_text.delete("1.0", tk.END)
        if self.eslint_running:
            # Nếu đang chạy thì yêu cầu hủy
            self.stop_loading()
            self.eslint_running = False
            self.update_eslint_button()
            return

        self.eslint_running = True
        self.update_eslint_button()
        self.start_loading()
        self._eslint_thread = threading.Thread(target=self._run_eslint_thread)
        self._eslint_thread.start()

    def _run_eslint_thread(self):
        try:
            run_eslint(self)
        finally:
            self.eslint_running = False
            self.stop_loading()
            self.update_eslint_button()

    def on_count_lines(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._count_lines_thread).start()

    def _count_lines_thread(self):
        try:
            count_lines(self)
        finally:
            self.stop_loading()

    def on_check_title_comment(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_title_comment_thread).start()

    def _check_title_comment_thread(self):
        try:
            check_title_comment(self)
        finally:
            self.stop_loading()

    def on_check_css_color(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_css_color_thread).start()

    def _check_css_color_thread(self):
        try:
            check_css_color_main(self)
        finally:
            self.stop_loading()

    def on_check_hardcode_jp(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_hardcode_jp_thread).start()

    def _check_hardcode_jp_thread(self):
        try:
            check_hardcode_jp(self)
        finally:
            self.stop_loading()

    def on_check_console(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_console_thread).start()

    def _check_console_thread(self):
        try:
            check_console_log(self)
        finally:
            self.stop_loading()

    def on_check_jsdoc(self):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("end", " Tính năng tạm ngừng\n", "warning")

    def on_check_vue_order(self):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("end", " Tính năng tạm ngừng\n", "warning")

    def on_check_english_comments(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_english_comments_thread).start()

    def _check_english_comments_thread(self):
        try:
            check_english_comments_main(self)
        finally:
            self.stop_loading()

    def on_check_hardcode_values(self):
        self.output_text.delete("1.0", tk.END)
        self.start_loading()
        threading.Thread(target=self._check_hardcode_values_thread).start()

    def _check_hardcode_values_thread(self):
        try:
            check_hardcoded_values_main(self)
        finally:
            self.stop_loading()

    def get_file_list(self):
        self.output_text.delete("1.0", tk.END)
        input_text = self.path_input.get("1.0", tk.END)
        files = [line.strip() for line in input_text.splitlines() if line.strip()]
        if not files:
            self.output_text.insert(tk.END, " Vui lòng nhập danh sách file.\n", "error")
        return files

    def display_output(self, text):
        for line in text.splitlines():
            tag = (
                "error"
                if any(keyword in line.lower() for keyword in ["error", "", ""])
                else None
            )
            # Fix text widget tag insertion - only pass tag if it's not None
            if tag:
                self.output_text.insert(tk.END, line + "\n", tag)
            else:
                self.output_text.insert(tk.END, line + "\n")

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
        for btn in self.buttons:
            # Không disable nút ESLint để có thể hủy tiến trình
            if "ESLint" in btn.cget("text"):
                continue
            btn.config(state=state)
        self.status_label.config(text=" Đang xử lý..." if running else " Sẵn sàng.")

    def update_eslint_button(self):
        for btn in self.buttons:
            if "ESLint" in btn.cget("text"):
                if self.eslint_running:
                    btn.config(text="⛔ Hủy ESLint")
                else:
                    btn.config(text=" Run ESLint")

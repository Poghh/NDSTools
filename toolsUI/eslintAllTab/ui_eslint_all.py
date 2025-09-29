import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import pandas as pd
from tkinterdnd2 import DND_FILES


class EslintAllTab:
    def __init__(self, tab_parent):
        self.tab = ttk.Frame(tab_parent, style="Custom.TFrame")
        tab_parent.add(self.tab, text="🔍 Check Eslint All")
        
        # State variables
        self.selfcheck_running = False
        self.eslint_running = False
        self.check_files_running = False
        self.folder_path = ""
        self.valid_file_paths = []  # Store valid file paths from selfcheck
        self.file_to_screen_map = {}  # Map file paths to screen names
        self.eslint_lock = Lock()  # Lock for thread-safe UI updates
        
        self.init_ui()

    def init_ui(self):
        # Style configuration
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

        self.root = self.tab

        # Main container
        main_frame = tk.Frame(self.root, bg="#f5f7fa")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Input section
        input_frame = ttk.LabelFrame(
            main_frame,
            text="📁 Cấu hình kiểm tra",
            padding=12,
            style="Custom.TLabelframe",
        )
        input_frame.pack(fill="x", pady=(0, 16))

        # Folder selection
        folder_frame = tk.Frame(input_frame, bg="#e3eafc")
        folder_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            folder_frame,
            text="📂 Folder chứa file selfcheck:",
            bg="#e3eafc",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.folder_btn = tk.Button(
            folder_frame,
            text="Chọn folder",
            command=self.select_folder,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#e3eafc",
            activeforeground="#0d47a1",
        )
        self.folder_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.folder_label = tk.Label(
            folder_frame,
            text="Chưa chọn folder",
            fg="gray",
            bg="#e3eafc",
            font=("Segoe UI", 10, "italic"),
        )
        self.folder_label.pack(side=tk.LEFT)

        # Two-column layout for screen names and document list (3-7 ratio)
        columns_frame = tk.Frame(input_frame, bg="#e3eafc")
        columns_frame.pack(fill="both", expand=True, pady=(0, 12))
        
        # Configure grid weights for 3-7 ratio with minimum width constraints
        columns_frame.grid_columnconfigure(0, weight=3, minsize=200)
        columns_frame.grid_columnconfigure(1, weight=7, minsize=400)
        columns_frame.grid_rowconfigure(0, weight=1)
        columns_frame.grid_rowconfigure(1, weight=0)  # For duplicate frame

        # Left column - Screen names (30% width)
        left_column = tk.Frame(columns_frame, bg="#e3eafc")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_column.grid_columnconfigure(0, weight=1)
        left_column.grid_rowconfigure(1, weight=1)  # For text input

        tk.Label(
            left_column,
            text="🖥️ Tên các màn hình:",
            bg="#e3eafc",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="nw", pady=(0, 5))

        self.screen_input = scrolledtext.ScrolledText(
            left_column,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.screen_input.grid(row=1, column=0, sticky="nsew")

        # Enable drag and drop for screen input
        try:
            drop_register = getattr(self.screen_input, 'drop_target_register', None)
            dnd_bind = getattr(self.screen_input, 'dnd_bind', None)
            if drop_register and dnd_bind:
                drop_register(DND_FILES)
                dnd_bind("<<Drop>>", self.handle_screen_drop)
        except (AttributeError, Exception):
            pass

        # Duplicate check section (below screen input)
        duplicate_frame = tk.Frame(columns_frame, bg="#e3eafc")
        duplicate_frame.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(8, 0))

        self.check_duplicate_btn = tk.Button(
            duplicate_frame,
            text="🗑️ Loại bỏ trùng & Sắp xếp",
            command=self.remove_duplicates,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#e3eafc",
            activeforeground="#0d47a1",
        )
        self.check_duplicate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.duplicate_status = tk.Label(
            duplicate_frame,
            text="",
            fg="gray",
            bg="#e3eafc",
            font=("Segoe UI", 10, "italic"),
        )
        self.duplicate_status.pack(side=tk.LEFT)

        # Right column - Document list (70% width)
        right_column = tk.Frame(columns_frame, bg="#e3eafc")
        right_column.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(6, 0))
        right_column.grid_columnconfigure(0, weight=1)
        right_column.grid_rowconfigure(1, weight=1)  # For text output
        right_column.grid_rowconfigure(2, weight=0)  # For check files button

        tk.Label(
            right_column,
            text="📄 Danh sách tài liệu:",
            bg="#e3eafc",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="nw", pady=(0, 5))

        self.doc_output = scrolledtext.ScrolledText(
            right_column,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
            state=tk.DISABLED,
        )
        self.doc_output.grid(row=1, column=0, sticky="nsew")

        # Check files button (below document list)
        check_files_frame = tk.Frame(right_column, bg="#e3eafc")
        check_files_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        self.check_files_btn = tk.Button(
            check_files_frame,
            text="📁 Kiểm tra file",
            command=self.check_files,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#e3eafc",
            activeforeground="#0d47a1",
        )
        self.check_files_btn.pack(side=tk.LEFT)

        # Buttons section
        button_frame = tk.Frame(main_frame, bg="#f5f7fa")
        button_frame.pack(fill="x", pady=(0, 16))

        # Check selfcheck button
        self.selfcheck_btn = tk.Button(
            button_frame,
            text="🔍 Kiểm tra file selfcheck",
            command=self.check_selfcheck,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#e3eafc",
            activeforeground="#0d47a1",
        )
        self.selfcheck_btn.pack(side=tk.LEFT, padx=(0, 16))

        # Check eslint button
        self.eslint_btn = tk.Button(
            button_frame,
            text="🚀 Kiểm tra ESLint",
            command=self.check_eslint,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#e3eafc",
            activeforeground="#0d47a1",
        )
        self.eslint_btn.pack(side=tk.LEFT, padx=(0, 16))

        # Clear all button
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear toàn bộ",
            command=self.clear_all,
            bg="#fff",
            fg="#222",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RIDGE,
            bd=1,
            activebackground="#ffebee",
            activeforeground="#d32f2f",
        )
        self.clear_btn.pack(side=tk.LEFT)

        # Results section
        results_frame = tk.Frame(main_frame, bg="#f5f7fa")
        results_frame.pack(fill="both", expand=True)

        # Selfcheck results
        selfcheck_result_frame = ttk.LabelFrame(
            results_frame,
            text="📋 Kết quả kiểm tra Selfcheck",
            padding=8,
            style="Custom.TLabelframe",
        )
        selfcheck_result_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 8))

        self.selfcheck_output = scrolledtext.ScrolledText(
            selfcheck_result_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.selfcheck_output.pack(fill="both", expand=True)

        # ESLint results
        eslint_result_frame = ttk.LabelFrame(
            results_frame,
            text="🚀 Kết quả kiểm tra ESLint",
            padding=8,
            style="Custom.TLabelframe",
        )
        eslint_result_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(8, 0))

        self.eslint_output = scrolledtext.ScrolledText(
            eslint_result_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fafdff",
            relief=tk.GROOVE,
            borderwidth=2,
        )
        self.eslint_output.pack(fill="both", expand=True)

        # Configure text tags for styling
        for output_widget in [self.selfcheck_output, self.eslint_output, self.doc_output]:
            output_widget.tag_configure("error", foreground="red", font=("Consolas", 10, "bold"))
            output_widget.tag_configure("success", foreground="green", font=("Consolas", 10, "bold"))
            output_widget.tag_configure("warning", foreground="#FF6600", font=("Consolas", 10, "bold"))
            output_widget.tag_configure("info", foreground="blue", font=("Consolas", 10, "bold"))

        # Progress bars
        self.selfcheck_progress = ttk.Progressbar(selfcheck_result_frame, mode="indeterminate", length=200)
        self.eslint_progress = ttk.Progressbar(eslint_result_frame, mode="indeterminate", length=200)

    def select_folder(self):
        """Select folder containing selfcheck files"""
        folder_path = filedialog.askdirectory(title="Chọn folder chứa file selfcheck")
        if folder_path:
            self.folder_path = folder_path
            folder_name = os.path.basename(folder_path)
            self.folder_label.config(text=f"📁 {folder_name}", fg="green")
        else:
            self.folder_label.config(text="Chưa chọn folder", fg="gray")

    def handle_screen_drop(self, event):
        """Handle drag and drop for screen names"""
        try:
            file_path = event.data
            if file_path.startswith("{"):
                file_path = file_path[1:-1]
            
            # If it's a text file, read and insert content
            if file_path.lower().endswith(('.txt', '.csv')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.screen_input.delete("1.0", tk.END)
                    self.screen_input.insert("1.0", content)
        except Exception as e:
            self.display_selfcheck_output(f"❌ Lỗi khi đọc file: {str(e)}", "error")

    def remove_duplicates(self):
        """Remove duplicates from screen names list and sort"""
        input_text = self.screen_input.get("1.0", tk.END).strip()
        if not input_text:
            self.duplicate_status.config(text="❌ Chưa có danh sách", fg="red")
            return
        
        # Get all lines and filter out empty lines
        all_lines = [line.strip() for line in input_text.splitlines() if line.strip()]
        
        if not all_lines:
            self.duplicate_status.config(text="❌ Danh sách trống", fg="red")
            return
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lines = []
        
        for line in all_lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        # Sort the unique lines in ascending order
        sorted_unique_lines = sorted(unique_lines)
        
        # Update the screen input with sorted unique lines
        self.screen_input.delete("1.0", tk.END)
        self.screen_input.insert("1.0", "\n".join(sorted_unique_lines))
        
        # Status update
        original_count = len(all_lines)
        unique_count = len(unique_lines)
        
        if original_count != unique_count:
            removed_count = original_count - unique_count
            self.duplicate_status.config(
                text=f"✅ Đã loại bỏ {removed_count} trùng & sắp xếp",
                fg="green"
            )
        else:
            self.duplicate_status.config(
                text="✅ Đã sắp xếp (không có trùng)",
                fg="blue"
            )

    def get_screen_names(self):
        """Get list of screen names from input"""
        input_text = self.screen_input.get("1.0", tk.END).strip()
        if not input_text:
            return []
        
        # Split by lines and filter empty lines
        all_lines = [line.strip() for line in input_text.splitlines() if line.strip()]
        
        # Remove duplicates while preserving order (silent processing)
        seen = set()
        unique_lines = []
        for line in all_lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        return unique_lines

    def clear_all(self):
        """Clear all data and reset to initial state"""
        # Clear folder path
        self.folder_path = ""
        self.folder_label.config(text="Chưa chọn folder", fg="gray")
        
        # Clear valid file paths
        self.valid_file_paths = []
        self.file_to_screen_map = {}
        
        # Clear screen input
        self.screen_input.delete("1.0", tk.END)
        
        # Clear document output
        self.doc_output.config(state=tk.NORMAL)
        self.doc_output.delete("1.0", tk.END)
        self.doc_output.config(state=tk.DISABLED)
        
        # Clear duplicate status
        self.duplicate_status.config(text="", fg="gray")
        
        # Clear results areas
        self.selfcheck_output.delete("1.0", tk.END)
        self.eslint_output.delete("1.0", tk.END)
        
        # Reset button states
        self.check_files_btn.config(text="📁 Kiểm tra file", state=tk.NORMAL)
        self.selfcheck_btn.config(text="🔍 Kiểm tra file selfcheck", state=tk.NORMAL)
        self.eslint_btn.config(text="🚀 Kiểm tra ESLint", state=tk.NORMAL)
        
        # Reset running states
        self.check_files_running = False
        self.selfcheck_running = False
        self.eslint_running = False

    def check_files(self):
        """Check files based on screen names"""
        if self.check_files_running:
            return
            
        if not self.folder_path:
            self.display_doc_output("❌ Vui lòng chọn folder chứa file selfcheck", "error")
            return
            
        screen_names = self.get_screen_names()
        if not screen_names:
            self.display_doc_output("❌ Vui lòng nhập tên các màn hình", "error")
            return

        self.check_files_running = True
        self.check_files_btn.config(text="⏳ Đang kiểm tra...", state=tk.DISABLED)
        
        # Clear doc output
        self.doc_output.config(state=tk.NORMAL)
        self.doc_output.delete("1.0", tk.END)
        
        # Run in separate thread
        threading.Thread(target=self._check_files_thread, args=(screen_names,)).start()

    def _check_files_thread(self, screen_names):
        """Thread function for checking files"""
        try:
            # Get all files in the folder and subfolders
            all_files = []
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            # Check each screen name
            results = []
            for screen_name in screen_names:
                found_files = []
                
                # Search for files containing the screen name
                for file_path in all_files:
                    file_name = os.path.basename(file_path)
                    # Check if screen name is in the file name (case insensitive)
                    if screen_name.lower() in file_name.lower():
                        relative_path = os.path.relpath(file_path, self.folder_path)
                        found_files.append(relative_path)
                
                if found_files:
                    # If multiple files found, show all
                    if len(found_files) == 1:
                        file_name = os.path.basename(found_files[0])
                        results.append(f"{screen_name} - {file_name}")
                    else:
                        file_name = os.path.basename(found_files[0])
                        results.append(f"{screen_name} - {file_name} (và {len(found_files)-1} file khác)")
                        for additional_file in found_files[1:]:
                            additional_file_name = os.path.basename(additional_file)
                            results.append(f"    └─ {additional_file_name}")
                else:
                    results.append(f"{screen_name} - Không tìm thấy file")
            
            # Display results directly without extra messages
            for result in results:
                if "Không tìm thấy file" in result:
                    self.display_doc_output(result, "error")
                elif "file khác" in result:
                    self.display_doc_output(result, "warning")
                elif result.startswith("    └─"):
                    self.display_doc_output(result, "info")
                else:
                    self.display_doc_output(result, "success")
            
        except Exception as e:
            self.display_doc_output(f"❌ Lỗi: {str(e)}", "error")
        finally:
            self.check_files_running = False
            self.check_files_btn.config(text="📁 Kiểm tra file", state=tk.NORMAL)

    def check_selfcheck(self):
        """Check selfcheck files"""
        if self.selfcheck_running:
            return
            
        if not hasattr(self, 'folder_path') or not self.folder_path:
            self.display_selfcheck_output("❌ Vui lòng chọn folder chứa file selfcheck", "error")
            return
            
        screen_names = self.get_screen_names()
        if not screen_names:
            self.display_selfcheck_output("❌ Vui lòng nhập tên các màn hình", "error")
            return

        self.selfcheck_running = True
        self.start_selfcheck_progress()
        self.selfcheck_btn.config(text="⏳ Đang kiểm tra...", state=tk.DISABLED)
        
        # Run in separate thread
        threading.Thread(target=self._check_selfcheck_thread, args=(screen_names,)).start()

    def _check_selfcheck_thread(self, screen_names):
        """Thread function for selfcheck"""
        try:
            # Get all files in the folder and subfolders
            all_files = []
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            # Initialize summary counters
            total_error_screens = 0
            total_missing_files = 0
            self.valid_file_paths = []  # Clear and store valid file paths for ESLint
            self.file_to_screen_map = {}  # Map file paths to screen names
            
            # Process each screen name
            for screen_name in screen_names:
                self.display_selfcheck_output(f"🔍 Kiểm tra màn hình: {screen_name}", "info")
                
                # Find files containing the screen name
                found_files = []
                for file_path in all_files:
                    file_name = os.path.basename(file_path)
                    if screen_name.lower() in file_name.lower() and file_name.lower().endswith(('.xlsx', '.xls')):
                        found_files.append(file_path)
                
                # Check file count
                screen_has_error = False
                if len(found_files) == 0:
                    self.display_selfcheck_output(f"❌ {screen_name}: Không tìm thấy file Excel", "error")
                    screen_has_error = True
                    continue
                elif len(found_files) > 1:
                    self.display_selfcheck_output(f"❌ {screen_name}: Tìm thấy {len(found_files)} file (cần đúng 1 file)", "error")
                    for f in found_files:
                        self.display_selfcheck_output(f"   - {os.path.basename(f)}", "warning")
                    screen_has_error = True
                    continue
                
                # Process the single file found
                excel_file = found_files[0]
                file_name = os.path.basename(excel_file)
                self.display_selfcheck_output(f"📁 {screen_name}: Đang xử lý {file_name}", "info")
                
                try:
                    # Read Excel file - sheet "機能別ソース一覧"
                    workbook = pd.read_excel(excel_file, sheet_name="機能別ソース一覧", header=None)
                    
                    # Extract paths where column D = "新規"
                    paths = []
                    for _index, row in workbook.iterrows():
                        try:
                            if pd.notna(row.iloc[3]) and str(row.iloc[3]).strip() == "新規":
                                if pd.notna(row.iloc[2]):
                                    path = str(row.iloc[2]).strip()
                                    if path:
                                        paths.append(path)
                        except (IndexError, Exception):
                            continue
                    
                    if not paths:
                        self.display_selfcheck_output(f"⚠️ {screen_name}: Không tìm thấy path nào có cột D = '新規'", "warning")
                        screen_has_error = True
                        continue
                    
                    self.display_selfcheck_output(f"📂 {screen_name}: Tìm thấy {len(paths)} path", "info")
                    
                    # Check if files exist
                    existing_count = 0
                    missing_count = 0
                    
                    for path in paths:
                        # Try different base directories
                        possible_paths = [
                            path,  # Absolute path
                            os.path.join(self.folder_path, path),  # Relative to selected folder
                            os.path.join(os.path.dirname(excel_file), path),  # Relative to Excel file
                        ]
                        
                        file_exists = False
                        for full_path in possible_paths:
                            if os.path.exists(full_path):
                                file_exists = True
                                break
                        
                        if file_exists:
                            existing_count += 1
                            # Add valid paths to ESLint list if they are JS/TS/Vue files
                            for full_path in possible_paths:
                                if os.path.exists(full_path):
                                    if any(full_path.lower().endswith(ext) for ext in ['.js', '.ts', '.vue', '.jsx', '.tsx']):
                                        self.valid_file_paths.append(full_path)
                                        self.file_to_screen_map[full_path] = screen_name
                                    break
                        else:
                            missing_count += 1
                            total_missing_files += 1
                            self.display_selfcheck_output(f"   ❌ Không tìm thấy: {path}", "error")
                    
                    # Summary for this screen
                    if missing_count == 0:
                        self.display_selfcheck_output(f"✅ {screen_name}: Tất cả {existing_count} file đều tồn tại", "success")
                    else:
                        self.display_selfcheck_output(f"⚠️ {screen_name}: {existing_count} file tồn tại, {missing_count} file thiếu", "warning")
                        screen_has_error = True
                
                except Exception as e:
                    self.display_selfcheck_output(f"❌ {screen_name}: Lỗi đọc Excel - {str(e)}", "error")
                    screen_has_error = True
                
                # Count error screens
                if screen_has_error:
                    total_error_screens += 1
                
                self.display_selfcheck_output("", "info")  # Empty line separator
            
            # Display summary
            self.display_selfcheck_output("=" * 60, "info")
            self.display_selfcheck_output("📊 TỔNG HỢP KẾT QUẢ:", "info")
            self.display_selfcheck_output(f"📋 Tổng số màn hình kiểm tra: {len(screen_names)}", "info")
            
            if total_error_screens == 0:
                self.display_selfcheck_output(f"✅ Tổng số màn hình lỗi: {total_error_screens}", "success")
            else:
                self.display_selfcheck_output(f"❌ Tổng số màn hình lỗi: {total_error_screens}", "error")
            
            if total_missing_files == 0:
                self.display_selfcheck_output(f"✅ Tổng số file path không tìm thấy: {total_missing_files}", "success")
            else:
                self.display_selfcheck_output(f"❌ Tổng số file path không tìm thấy: {total_missing_files}", "error")
            
            self.display_selfcheck_output("=" * 60, "info")
            
            # Show ESLint file count info
            if self.valid_file_paths:
                unique_eslint_files = len(set(self.valid_file_paths))
                self.display_selfcheck_output(f"📂 Đã lưu {unique_eslint_files} file JS/TS/Vue hợp lệ để chạy ESLint", "info")
            else:
                self.display_selfcheck_output("ℹ️ Không có file JS/TS/Vue hợp lệ để chạy ESLint", "warning")
            
            self.display_selfcheck_output("✅ Hoàn thành kiểm tra selfcheck", "success")
            
        except Exception as e:
            self.display_selfcheck_output(f"❌ Lỗi tổng quát: {str(e)}", "error")
        finally:
            self.selfcheck_running = False
            self.stop_selfcheck_progress()
            self.selfcheck_btn.config(text="🔍 Kiểm tra file selfcheck", state=tk.NORMAL)

    def check_eslint(self):
        """Check ESLint for valid files from selfcheck"""
        if self.eslint_running:
            return
        
        if not self.valid_file_paths:
            self.display_eslint_output("❌ Vui lòng chạy kiểm tra Selfcheck trước để lấy danh sách file hợp lệ", "error")
            return

        self.eslint_running = True
        self.start_eslint_progress()
        self.eslint_btn.config(text="⏳ Đang kiểm tra...", state=tk.DISABLED)
        
        # Run in separate thread
        threading.Thread(target=self._check_eslint_thread).start()

    def _check_eslint_thread(self):
        """Thread function for ESLint check using multithreading"""
        try:
            self.display_eslint_output("🚀 Bắt đầu kiểm tra ESLint cho các file hợp lệ...\n", "info")
            
            # Prepare file list with screen mapping
            file_tasks = []
            seen_files = set()
            
            for file_path in self.valid_file_paths:
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    screen_name = self.file_to_screen_map.get(file_path, "Unknown")
                    file_tasks.append((file_path, screen_name))
            
            total_files = len(file_tasks)
            self.display_eslint_output(f"📁 Tìm thấy {total_files} file JS/TS/Vue từ Selfcheck để kiểm tra", "info")
            
            # Auto-detect optimal number of workers based on system specs
            max_workers = self._get_optimal_workers()
            self.display_eslint_output(f"⏳ Đang chạy ESLint song song ({max_workers} luồng)...\n", "info")
            
            # Run ESLint in parallel using ThreadPoolExecutor
            results = []
            completed_count = 0
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_task = {
                    executor.submit(self._run_eslint_single_file, file_path, screen_name): (file_path, screen_name)
                    for file_path, screen_name in file_tasks
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_task):
                    completed_count += 1
                    result = future.result()
                    results.append(result)
                    
                    # Update progress
                    with self.eslint_lock:
                        self.display_eslint_output(f"⏳ Hoàn thành: {completed_count}/{total_files} file", "info")
            
            # Group results by screen and display errors only
            screen_errors = {}
            total_error_files = 0
            
            for result in results:
                screen_name = result['screen_name']
                if not result['success']:
                    if screen_name not in screen_errors:
                        screen_errors[screen_name] = []
                    
                    error_info = {
                        'display_path': result['display_path'],
                        'stdout': result['stdout'],
                        'stderr': result['stderr'],
                        'exception': result.get('exception', False)
                    }
                    screen_errors[screen_name].append(error_info)
                    total_error_files += 1
            
            # Display results
            self.display_eslint_output("\n" + "=" * 60, "info")
            
            if not screen_errors:
                self.display_eslint_output("✅ TẤT CẢ FILE ĐỀU PASS ESLINT!", "success")
            else:
                self.display_eslint_output("❌ CÁC MÀN HÌNH CÓ LỖI ESLINT:", "error")
                self.display_eslint_output("", "info")
                
                for screen_name in sorted(screen_errors.keys()):
                    error_list = screen_errors[screen_name]
                    self.display_eslint_output(f"Màn hình {screen_name}:", "error")
                    
                    for error in error_list:
                        if error.get('exception'):
                            self.display_eslint_output(f"  - Lỗi chạy ESLint ở {error['display_path']}: {error['stderr']}", "error")
                        else:
                            self.display_eslint_output(f"  - Lỗi ESLint ở {error['display_path']}:", "error")
                            if error['stdout']:
                                # Indent the ESLint output for better readability
                                indented_output = '\n'.join(f"    {line}" for line in error['stdout'].split('\n') if line.strip())
                                self.display_eslint_output(indented_output, "warning")
                            if error['stderr']:
                                indented_error = '\n'.join(f"    {line}" for line in error['stderr'].split('\n') if line.strip())
                                self.display_eslint_output(indented_error, "error")
                    
                    self.display_eslint_output("", "info")
            
            # Summary
            self.display_eslint_output("📊 TỔNG HỢP ESLINT:", "info")
            self.display_eslint_output(f"📋 Tổng số file kiểm tra: {total_files}", "info")
            
            if total_error_files == 0:
                self.display_eslint_output(f"✅ File có lỗi ESLint: {total_error_files}", "success")
            else:
                self.display_eslint_output(f"❌ File có lỗi ESLint: {total_error_files}", "error")
            
            success_files = total_files - total_error_files
            self.display_eslint_output(f"✅ File pass ESLint: {success_files}", "success")
            
            self.display_eslint_output("=" * 60, "info")
            self.display_eslint_output("✅ Hoàn thành kiểm tra ESLint", "success")
            
        except Exception as e:
            self.display_eslint_output(f"❌ Lỗi: {str(e)}", "error")
        finally:
            self.eslint_running = False
            self.stop_eslint_progress()
            self.eslint_btn.config(text="🚀 Kiểm tra ESLint", state=tk.NORMAL)

    def _clean_display_path(self, path):
        """Clean up display path to remove unnecessary ..\ and show meaningful path"""
        # Convert to forward slashes for easier processing
        normalized_path = path.replace('\\', '/')
        
        # Look for meaningful directory names to start from
        meaningful_dirs = ['client_cmn', 'src', 'components', 'pages', 'assets', 'utils', 'services', 'views']
        
        for dir_name in meaningful_dirs:
            if f'/{dir_name}/' in normalized_path:
                # Find the index where this directory starts
                start_index = normalized_path.find(f'/{dir_name}/')
                if start_index != -1:
                    clean_path = normalized_path[start_index + 1:]  # +1 to remove leading /
                    return clean_path.replace('/', '\\')  # Convert back to Windows path style
        
        # If no meaningful directory found, remove leading ../ patterns
        while normalized_path.startswith('../'):
            normalized_path = normalized_path[3:]
        
        return normalized_path.replace('/', '\\')

    def _get_optimal_workers(self):
        """Calculate optimal number of worker threads based on system specs"""
        import os
        
        try:
            # Get CPU count
            cpu_count = os.cpu_count() or 4
            
            # For ESLint (CPU + I/O intensive), use CPU cores * 2-3
            # But with 32GB RAM, we can be more aggressive
            optimal_workers = cpu_count * 3
            
            # Ensure minimum 8 workers for good parallelization
            # Cap at 20 to reduce heat generation (reduced by 4 from 24)
            optimal_workers = max(8, min(optimal_workers, 20))
            
            return optimal_workers
            
        except Exception:
            return 12

    def _run_eslint_single_file(self, file_path, screen_name):
        """Run ESLint on a single file and return result"""
        try:
            relative_path = os.path.relpath(file_path, self.folder_path)
            display_path = self._clean_display_path(relative_path)
            
            result = subprocess.run(
                ["npx", "eslint", "--no-warn-ignored", file_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                shell=True,
                cwd=os.getcwd(),
            )
            
            return {
                'file_path': file_path,
                'display_path': display_path,
                'screen_name': screen_name,
                'return_code': result.returncode,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'display_path': self._clean_display_path(os.path.relpath(file_path, self.folder_path)),
                'screen_name': screen_name,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'exception': True
            }

    def display_selfcheck_output(self, text, tag=None):
        """Display text in selfcheck output area"""
        def update_ui():
            if tag:
                self.selfcheck_output.insert(tk.END, text + "\n", tag)
            else:
                self.selfcheck_output.insert(tk.END, text + "\n")
            self.selfcheck_output.see(tk.END)
        
        # Schedule UI update in main thread
        self.root.after(0, update_ui)

    def display_eslint_output(self, text, tag=None):
        """Display text in eslint output area"""
        def update_ui():
            if tag:
                self.eslint_output.insert(tk.END, text + "\n", tag)
            else:
                self.eslint_output.insert(tk.END, text + "\n")
            self.eslint_output.see(tk.END)
        
        # Schedule UI update in main thread
        self.root.after(0, update_ui)

    def display_doc_output(self, text, tag=None):
        """Display text in document output area"""
        def update_ui():
            self.doc_output.config(state=tk.NORMAL)
            if tag:
                self.doc_output.insert(tk.END, text + "\n", tag)
            else:
                self.doc_output.insert(tk.END, text + "\n")
            self.doc_output.see(tk.END)
            self.doc_output.config(state=tk.DISABLED)
        
        # Schedule UI update in main thread
        self.root.after(0, update_ui)

    def start_selfcheck_progress(self):
        """Start selfcheck progress bar"""
        self.selfcheck_progress.pack(pady=(0, 5))
        self.selfcheck_progress.start(10)

    def stop_selfcheck_progress(self):
        """Stop selfcheck progress bar"""
        self.selfcheck_progress.stop()
        self.selfcheck_progress.pack_forget()

    def start_eslint_progress(self):
        """Start eslint progress bar"""
        self.eslint_progress.pack(pady=(0, 5))
        self.eslint_progress.start(10)

    def stop_eslint_progress(self):
        """Stop eslint progress bar"""
        self.eslint_progress.stop()
        self.eslint_progress.pack_forget()

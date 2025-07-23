import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from toolsAction.utAction.copy_data import copy_data_action, validate_file_compatibility, get_copy_preview, copy_action_data, get_action_copy_preview

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class UnitTestTab:
    def __init__(self, tab_parent):
        # Create regular tkinter frame for tab
        self.tab = tk.Frame(tab_parent, bg="#f5f7fa")
        tab_parent.add(self.tab, text="🧪 Unit Test")
        
        # Store file paths for actions
        self.test_file_path = None
        self.doc_file_path = None
        
        # Store current action type
        self.current_action = None
        
        self.init_ui()

    def init_ui(self):
        # === Main container ===
        self.tab.columnconfigure(0, weight=1)
        self.tab.columnconfigure(1, weight=1)
        # Allow preview section to expand
        self.tab.rowconfigure(2, weight=1)

        # === Left Section - Mock Documentation Upload ===
        left_frame = ctk.CTkFrame(self.tab, corner_radius=16, height=120)
        left_frame.grid(row=0, column=0, sticky="new", padx=8, pady=(16, 8))
        left_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_propagate(False)

        # Left section header
        ctk.CTkLabel(
            left_frame,
            text="Tải file tài liệu mocks",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 8), sticky="w")

        # Upload button for mock documentation
        self.upload_test_btn = ctk.CTkButton(
            left_frame,
            text="Chọn file",
            command=self.upload_test_file,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.upload_test_btn.grid(row=1, column=0, padx=(16, 8), pady=8, sticky="w")

        # Status label for mock documentation
        self.test_file_label = ctk.CTkLabel(
            left_frame,
            text="Chưa chọn file",
            font=ctk.CTkFont(size=12),
            text_color="#16a34a",
            anchor="w"
        )
        self.test_file_label.grid(row=1, column=1, padx=(0, 16), pady=8, sticky="ew")

        # === Right Section - Unit Test File Upload ===
        right_frame = ctk.CTkFrame(self.tab, corner_radius=16, height=120)
        right_frame.grid(row=0, column=1, sticky="new", padx=8, pady=(16, 8))
        right_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_propagate(False)

        # Right section header
        ctk.CTkLabel(
            right_frame,
            text="Tải file unit test",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 8), sticky="w")

        # Upload button for unit test file
        self.upload_doc_btn = ctk.CTkButton(
            right_frame,
            text="Chọn tài liệu",
            command=self.upload_documentation,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.upload_doc_btn.grid(row=1, column=0, padx=(16, 8), pady=8, sticky="w")

        # Status label for unit test file
        self.doc_label = ctk.CTkLabel(
            right_frame,
            text="Chưa chọn tài liệu",
            font=ctk.CTkFont(size=12),
            text_color="#16a34a",
            anchor="w"
        )
        self.doc_label.grid(row=1, column=1, padx=(0, 16), pady=8, sticky="ew")

        # === Action Section ===
        action_frame = ctk.CTkFrame(self.tab, corner_radius=16, height=80)
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 8))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        action_frame.grid_propagate(False)

        # Copy data button (first action)
        self.copy_data_btn = ctk.CTkButton(
            action_frame,
            text="Sao chép dữ liệu 項目一覧",
            command=self.copy_data,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.copy_data_btn.grid(row=0, column=0, padx=(20, 8), pady=20)

        # Copy action data button (second action)
        self.copy_action_btn = ctk.CTkButton(
            action_frame,
            text="Sao chép dữ liệu アクション一覧",
            command=self.copy_action_data,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#16a34a",
            hover_color="#15803d"
        )
        self.copy_action_btn.grid(row=0, column=1, padx=(8, 20), pady=20)

        # === Preview Section (initially hidden) ===
        self.preview_frame = ctk.CTkFrame(self.tab, corner_radius=16)
        self.preview_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 16))
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_remove()  # Hide initially

        # Preview header
        preview_header_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        preview_header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        preview_header_frame.grid_columnconfigure(0, weight=1)

        self.preview_header_label = ctk.CTkLabel(
            preview_header_frame,
            text="Preview - Sao chép dữ liệu",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preview_header_label.grid(row=0, column=0, sticky="w")

        # Close preview button
        self.close_preview_btn = ctk.CTkButton(
            preview_header_frame,
            text="X",
            command=self.hide_preview,
            height=32,
            width=36,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        self.close_preview_btn.grid(row=0, column=1, sticky="e")

        # Preview text
        self.preview_text = ctk.CTkTextbox(
            self.preview_frame, 
            height=250,
            font=ctk.CTkFont(size=11)
        )
        self.preview_text.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 8), sticky="ew")

        # Preview buttons frame
        preview_button_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        preview_button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))
        preview_button_frame.grid_columnconfigure(0, weight=1)

        # Proceed button
        self.proceed_btn = ctk.CTkButton(
            preview_button_frame,
            text="Tiến hành sao chép",
            command=self.proceed_copy,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#16a34a",
            hover_color="#15803d"
        )
        self.proceed_btn.grid(row=0, column=0, padx=(0, 8), sticky="w")

        # Cancel button  
        self.cancel_btn = ctk.CTkButton(
            preview_button_frame,
            text="Hủy bỏ",
            command=self.hide_preview,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        self.cancel_btn.grid(row=0, column=1, padx=(8, 0), sticky="w")

    def upload_test_file(self):
        """Upload mock documentation file"""
        file_path = filedialog.askopenfilename(
            title="Chọn file tài liệu mocks",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All Test Files", "*.java *.py *.js *.ts *.txt"),
                ("Java files", "*.java"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("TypeScript files", "*.ts"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                import os
                file_name = os.path.basename(file_path)
                self.test_file_path = file_path  # Store full path
                self.test_file_label.configure(text=f"{file_name}")
                
                # Check compatibility if both files are loaded
                if self.doc_file_path:
                    self._check_compatibility()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file:\n{str(e)}")

    def upload_documentation(self):
        """Upload unit test file"""
        file_path = filedialog.askopenfilename(
            title="Chọn file unit test",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("Document files", "*.docx *.doc *.pdf *.txt"),
                ("Word files", "*.docx *.doc"),
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                import os
                file_name = os.path.basename(file_path)
                self.doc_file_path = file_path  # Store full path
                self.doc_label.configure(text=f"{file_name}")
                
                # Check compatibility if both files are loaded
                if self.test_file_path:
                    self._check_compatibility()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc tài liệu:\n{str(e)}")

    def _check_compatibility(self):
        """Check if uploaded files are compatible"""
        if self.test_file_path and self.doc_file_path:
            try:
                result = validate_file_compatibility(self.test_file_path, self.doc_file_path)
                if not result["compatible"]:
                    messagebox.showwarning("Cảnh báo tương thích", result["message"])
            except Exception as e:
                print(f"Error checking compatibility: {e}")

    def copy_action_data(self):
        """Copy action data from アクション一覧 sheet"""
        # Check if both files are uploaded
        if not self.test_file_path:
            messagebox.showwarning("Thiếu file", "Vui lòng tải file tài liệu mocks trước!")
            return
        
        if not self.doc_file_path:
            messagebox.showwarning("Thiếu tài liệu", "Vui lòng tải file unit test trước!")
            return
        
        try:
            # Update preview header for action copy
            self.preview_header_label.configure(text="Preview - Sao chép dữ liệu アクション一覧")
            
            # Show preview in the frame
            preview = get_action_copy_preview(self.test_file_path, self.doc_file_path)
            
            # Clear and populate preview text
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", preview)
            self.preview_text.configure(state="disabled")
            
            # Show preview frame and store action type
            self.current_action = "action_copy"
            self.preview_frame.grid()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị preview:\n{str(e)}")

    def copy_data(self):
        """Copy data from unit test file to mock documentation file"""
        # Check if both files are uploaded
        if not self.test_file_path:
            messagebox.showwarning("Thiếu file", "Vui lòng tải file tài liệu mocks trước!")
            return
        
        if not self.doc_file_path:
            messagebox.showwarning("Thiếu tài liệu", "Vui lòng tải file unit test trước!")
            return
        
        try:
            # Update preview header for data copy
            self.preview_header_label.configure(text="Preview - Sao chép dữ liệu 項目一覧")
            
            # Show preview in the frame
            preview = get_copy_preview(self.test_file_path, self.doc_file_path)
            
            # Clear and populate preview text
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", preview)
            self.preview_text.configure(state="disabled")
            
            # Show preview frame and store action type
            self.current_action = "data_copy"
            self.preview_frame.grid()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị preview:\n{str(e)}")

    def hide_preview(self):
        """Hide the preview frame"""
        self.preview_frame.grid_remove()

    def proceed_copy(self):
        """Proceed with the copy operation"""
        self.hide_preview()
        self._execute_copy()

    def _execute_copy(self):
        """Execute the actual copy operation"""
        try:
            def progress_update(message):
                # You could add a progress bar here if needed
                print(f"Progress: {message}")
            
            # Execute the appropriate copy action based on current_action
            if self.current_action == "action_copy":
                result = copy_action_data(
                    self.test_file_path, 
                    self.doc_file_path, 
                    progress_callback=progress_update
                )
                
                # Show success message for action copy
                success_msg = f"""
✅ Sao chép dữ liệu Action hoàn tất!

📁 File mocks (nguồn): {result['test_file']}
📄 File unit test (đích): {result['doc_file']}
📋 Sheet: {result['sheet_name']}
📍 Header tìm thấy tại: {result['header_found_at']}
📊 Dữ liệu đã copy: {result['data_copied']} items
📥 Paste vào: {result['paste_location']}
🆕 Header tạo mới: {'Có' if result['dest_header_created'] else 'Không'}
🎯 Cột アクション: {'Tìm thấy' if result['action_column_found'] else 'Không tìm thấy'}
📋 Copy sang cột: {result['target_columns_created']}
📊 Dữ liệu アクション: {result['action_data_copied']} items
🔧 Cột 処理条件: {'Tìm thấy' if result['condition_column_found'] else 'Không tìm thấy'}
📋 Copy sang: {result['condition_target_created']}
📊 Dữ liệu 処理条件: {result['condition_data_copied']} items
🌐 Cột API URL: {'Tìm thấy' if result['api_column_found'] else 'Không tìm thấy'}
📋 Copy sang: {result['webapi_target_created']}
📊 Dữ liệu API URL: {result['api_data_copied']} items
🔢 Cột 処理No.: {'Tìm thấy' if result['shori_no_column_found'] else 'Không tìm thấy'}
📋 Copy sang: {result['no_target_created']}
📊 Dữ liệu 処理No.: {result['shori_no_data_copied']} items
🔗 Cột kết hợp: {'Tìm thấy cả 2' if result['combined_columns_found'] else 'Không đủ cột'}
📋 Copy sang: {result['soutei_target_created']}
📊 Dữ liệu kết hợp: {result['combined_data_copied']} items
📝 Cột đã điền: {', '.join(result['additional_condition_columns_filled'])}
🔲 Cột border: {', '.join(result['border_only_columns_processed'])}
✅ Trạng thái: {result['status']}
                """
            else:
                # Default to data copy (original functionality)
                result = copy_data_action(
                    self.test_file_path, 
                    self.doc_file_path, 
                    progress_callback=progress_update
                )
                
                # Show success message for data copy
                success_msg = f"""
✅ Sao chép dữ liệu hoàn tất!

📁 File mocks (nguồn): {result['test_file']}
📄 File unit test (đích): {result['doc_file']}
📋 Sheet: {result['sheet_name']}
📊 Dữ liệu đã copy: {result['rows_copied']} dòng × {result['cols_copied']} cột
📤 Copy từ: dòng {result['source_start_row']} (file mocks)
📥 Paste vào: dòng {result['paste_start_row']} (file unit test)
🔲 Border: Đã thêm outside border bao quanh dữ liệu
📋 Data_1 sheet: {'Đã copy thành công' if result['data_1_copied'] else 'Không tìm thấy sheet data_1'}
📍 Vị trí data_1: dòng {result['data_1_start_row']}, cột {result['data_1_start_col']}
📄 Bảng borders: Đã thêm từ dòng {result['table_start_row']} đến {result['table_end_row']}
🗑️ Clean up: Đã xóa sheet data_1 sau khi copy
✅ Trạng thái: {result['status']}
                """
            
            messagebox.showinfo("Thành công", success_msg.strip())
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sao chép dữ liệu:\n{str(e)}") 
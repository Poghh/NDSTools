import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox

import customtkinter as ctk
from toolsAction.utAction.excel_formatter import process_screen_folders, validate_inputs

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class FormatExcelTab:
    def __init__(self, tab_parent):
        # Create regular tkinter frame for tab
        self.tab = tk.Frame(tab_parent, bg="#f5f7fa")
        tab_parent.add(self.tab, text="📊 Format Excel")
        
        # State variables
        self.base_folder_path = ""
        self.processing = False
        self.process_thread = None
        
        self.init_ui()

    def init_ui(self):
        # === Main container ===
        self.tab.columnconfigure(0, weight=1)
        self.tab.rowconfigure(2, weight=1)  # Output area expands

        # === Header Section ===
        header_frame = ctk.CTkFrame(self.tab, corner_radius=16, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)

        # Title and description
        ctk.CTkLabel(
            header_frame,
            text="📊 Format Excel Files",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 4), sticky="w")

        # Kiểm tra xlwings availability
        try:
            import xlwings
            method_text = "Sử dụng xlwings -  linked objects/images"
            method_color = "green"
        except ImportError:
            method_text = "Sử dụng openpyxl - có thể ảnh hưởng linked objects"
            method_color = "orange"
        
        ctk.CTkLabel(
            header_frame,
            text=method_text,
            font=ctk.CTkFont(size=12),
            text_color=method_color
        ).grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="w")

        # === Input Section ===
        input_frame = ctk.CTkFrame(self.tab, corner_radius=16)
        input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        input_frame.grid_columnconfigure(1, weight=1)

        # Screen list input
        ctk.CTkLabel(
            input_frame,
            text="Danh sách màn hình:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nw")

        # Screen list text area
        self.screen_text = tk.Text(
            input_frame,
            height=6,
            width=50,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.screen_text.grid(row=0, column=1, padx=(8, 16), pady=(16, 8), sticky="ew")

        # Placeholder text
        placeholder_text = "Nhập danh sách màn hình (mỗi dòng một màn hình hoặc cách nhau bằng dấu phẩy):\n\nVí dụ:\nSCR001\nSCR002, SCR003\nSCR004"
        self.screen_text.insert("1.0", placeholder_text)
        self.screen_text.config(fg="gray")

        # Bind events for placeholder
        self.screen_text.bind("<FocusIn>", self.on_screen_text_focus_in)
        self.screen_text.bind("<FocusOut>", self.on_screen_text_focus_out)

        # Base folder selection
        folder_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(8, 16))
        folder_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            folder_frame,
            text="Folder tổng:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=(0, 8), pady=8, sticky="w")

        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text="Chưa chọn folder",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        self.folder_label.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.select_folder_btn = ctk.CTkButton(
            folder_frame,
            text="📁 Chọn Folder",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            command=self.select_base_folder
        )
        self.select_folder_btn.grid(row=0, column=2, padx=(8, 0), pady=8)

        # Options (chỉ hiển thị khi dùng openpyxl)
        self.xlwings_available = False
        try:
            import xlwings
            self.xlwings_available = True
        except ImportError:
            pass
        
        if not self.xlwings_available:
            options_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
            options_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=(8, 8))

            self.force_format_var = tk.BooleanVar(value=True)
            self.force_format_cb = ctk.CTkCheckBox(
                options_frame,
                text="🚨 Force Format (xử lý dù có linked objects - có thể mất data)",
                font=ctk.CTkFont(size=12),
                variable=self.force_format_var,
                text_color="red"
            )
            self.force_format_cb.pack(side="left")
        else:
            # Nếu có xlwings, không cần force format option
            self.force_format_var = tk.BooleanVar(value=False)

        # Action buttons
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, padx=16, pady=(8, 16))

        self.process_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Bắt Đầu Format",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            command=self.start_processing
        )
        self.process_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Xóa Log",
            font=ctk.CTkFont(size=12),
            width=100,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear_output
        )
        self.clear_btn.pack(side="left", padx=8)

        # === Output Section ===
        output_frame = ctk.CTkFrame(self.tab, corner_radius=16)
        output_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        # Output header
        ctk.CTkLabel(
            output_frame,
            text="📋 Kết quả xử lý:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=("Consolas", 10),
            bg="black",
            fg="lightgreen",
            insertbackground="white",
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        self.output_text.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

        # Initial message
        self.output_text.insert(tk.END, "💡 Sẵn sàng format Excel files...\n")
        self.output_text.insert(tk.END, "📝 Nhập danh sách màn hình và chọn folder để bắt đầu.\n\n")

    def on_screen_text_focus_in(self, event):
        """Xử lý khi focus vào text area"""
        if self.screen_text.get("1.0", tk.END).strip().startswith("Nhập danh sách"):
            self.screen_text.delete("1.0", tk.END)
            self.screen_text.config(fg="black")

    def on_screen_text_focus_out(self, event):
        """Xử lý khi focus ra khỏi text area"""
        if not self.screen_text.get("1.0", tk.END).strip():
            placeholder_text = "Nhập danh sách màn hình (mỗi dòng một màn hình hoặc cách nhau bằng dấu phẩy):\n\nVí dụ:\nSCR001\nSCR002, SCR003\nSCR004"
            self.screen_text.insert("1.0", placeholder_text)
            self.screen_text.config(fg="gray")

    def select_base_folder(self):
        """Chọn folder tổng"""
        folder_path = filedialog.askdirectory(
            title="Chọn folder tổng chứa các folder màn hình"
        )
        
        if folder_path:
            self.base_folder_path = folder_path
            # Hiển thị tên folder (không hiển thị đường dẫn đầy đủ để gọn)
            folder_name = os.path.basename(folder_path)
            self.folder_label.configure(
                text=f"📁 {folder_name}",
                text_color="blue"
            )
            
            self.append_output(f"📁 Đã chọn folder: {folder_path}\n")

    def start_processing(self):
        """Bắt đầu xử lý format Excel"""
        if self.processing:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi...")
            return

        # Validate input
        screen_text = self.screen_text.get("1.0", tk.END)
        is_valid, error_msg, screen_list = validate_inputs(screen_text, self.base_folder_path)
        
        if not is_valid:
            messagebox.showerror("Lỗi", error_msg)
            return

        # Get force_format option
        force_format = self.force_format_var.get()
        
        # Confirm action
        if self.xlwings_available:
            method_msg = "xlwings -  linked objects"
            confirm_msg = f"Sẽ xử lý {len(screen_list)} màn hình trong folder:\n{self.base_folder_path}\n\n✅  {method_msg}\n\nTiếp tục?"
        else:
            force_msg = "BẬT (có thể mất linked objects)" if force_format else "TẮT (bỏ qua file có objects)"
            confirm_msg = f"Sẽ xử lý {len(screen_list)} màn hình trong folder:\n{self.base_folder_path}\n\n🚨 Force Format: {force_msg}\n\nTiếp tục?"
        
        if not messagebox.askyesno("Xác nhận", confirm_msg):
            return

        # Start processing in background thread
        self.processing = True
        self.process_btn.configure(text="⏳ Đang xử lý...", state="disabled")
        
        self.append_output(f"\n{'='*60}\n")
        self.append_output(f"🚀 Bắt đầu xử lý {len(screen_list)} màn hình...\n")
        self.append_output(f"📁 Folder gốc: {self.base_folder_path}\n")
        self.append_output(f"📋 Danh sách màn hình: {', '.join(screen_list)}\n")
        
        if self.xlwings_available:
            self.append_output(f"✅  xlwings -  linked objects\n")
        else:
            force_msg = "BẬT (có thể mất linked objects)" if force_format else "TẮT (bỏ qua file có objects)"
            self.append_output(f"🚨 Force Format: {force_msg}\n")
        
        self.append_output(f"{'='*60}\n\n")

        # Run in thread
        self.process_thread = threading.Thread(
            target=self.process_excel_files,
            args=(screen_list, force_format),
            daemon=True
        )
        self.process_thread.start()

    def process_excel_files(self, screen_list, force_format):
        """Xử lý format Excel files trong background thread"""
        try:
            # Process files
            results = process_screen_folders(
                screen_list, 
                self.base_folder_path, 
                self.append_output,
                force_format
            )
            
            # Summary
            total_success = sum(r['success_count'] for r in results.values())
            total_error = sum(r['error_count'] for r in results.values())
            
            self.append_output(f"\n{'='*60}\n")
            self.append_output(f"🎉 HOÀN THÀNH!\n")
            self.append_output(f"📊 Tổng kết:\n")
            self.append_output(f"  ✅ Thành công: {total_success} file\n")
            self.append_output(f"  ❌ Lỗi: {total_error} file\n")
            self.append_output(f"  📂 Folder xử lý: {len(results)}\n")
            self.append_output(f"{'='*60}\n")
            
        except Exception as e:
            self.append_output(f"\n❌ Lỗi không mong muốn: {str(e)}\n")
        
        finally:
            # Reset UI state
            self.tab.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """Reset UI về trạng thái ban đầu"""
        self.processing = False
        self.process_btn.configure(text="🚀 Bắt Đầu Format", state="normal")

    def append_output(self, text):
        """Thêm text vào output area (thread-safe)"""
        def update_ui():
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.update()
        
        # Schedule UI update in main thread
        self.tab.after(0, update_ui)

    def clear_output(self):
        """Xóa nội dung output"""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "💡 Đã xóa log. Sẵn sàng cho lần xử lý tiếp theo...\n\n")

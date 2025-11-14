import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import customtkinter as ctk
import pandas as pd

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CareBaseTab:
    def __init__(self, tab_parent):
        # Create regular tkinter frame for tab
        self.tab = tk.Frame(tab_parent, bg="#f5f7fa")
        tab_parent.add(self.tab, text="Handle CareBase Issues")

        # State variables
        self.file_path = ""
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
            header_frame, text=" Handle CareBase Issues", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Tải lên file Excel hoặc CSV để xử lý dữ liệu CareBase",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="w")

        # === Input Section ===
        input_frame = ctk.CTkFrame(self.tab, corner_radius=16)
        input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        input_frame.grid_columnconfigure(1, weight=1)

        # File input
        ctk.CTkLabel(
            input_frame, text="File Excel/CSV:", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nw")

        # File selection frame
        file_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        file_frame.grid(row=0, column=1, sticky="ew", padx=(8, 16), pady=(16, 8))
        file_frame.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="Chưa chọn file",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        self.file_label.grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

        self.select_file_btn = ctk.CTkButton(
            file_frame,
            text=" Chọn File",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            command=self.select_file,
        )
        self.select_file_btn.grid(row=1, column=0, padx=(8, 8), pady=(0, 8), sticky="w")

        # Action buttons
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=(8, 16))

        self.process_btn = ctk.CTkButton(
            button_frame,
            text=" Bắt Đầu Xử Lý",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            command=self.start_processing,
        )
        self.process_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            button_frame,
            text=" Xóa Log",
            font=ctk.CTkFont(size=12),
            width=100,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear_output,
        )
        self.clear_btn.pack(side="left", padx=8)

        # === Output Section ===
        output_frame = ctk.CTkFrame(self.tab, corner_radius=16)
        output_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        # Output header
        ctk.CTkLabel(
            output_frame, text="📋 Kết quả xử lý:", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=("Consolas", 10),
            bg="black",
            fg="lightgreen",
            insertbackground="white",
            wrap=tk.WORD,
            state=tk.NORMAL,
        )
        self.output_text.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

        # Initial message
        self.output_text.insert(tk.END, "💡 Sẵn sàng xử lý CareBase Issues...\n")
        self.output_text.insert(tk.END, " Tải lên file Excel hoặc CSV để bắt đầu.\n\n")

    def select_file(self):
        """Chọn file Excel hoặc CSV"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel hoặc CSV",
            filetypes=[
                ("All files", "*.*"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
            ],
        )

        if file_path:
            self.file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.configure(text=f" {file_name}", text_color="blue")

            self.append_output(f" ✅ Đã chọn file: {file_name}\n")
            self.append_output(f" 📁 Đường dẫn: {file_path}\n\n")

    def start_processing(self):
        """Bắt đầu xử lý file Excel hoặc CSV"""
        if self.processing:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi...")
            return

        if not self.file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file Excel hoặc CSV trước!")
            return

        if not os.path.exists(self.file_path):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return

        # Confirm action
        if not messagebox.askyesno(
            "Xác nhận", f"Sẽ xử lý file:\n{os.path.basename(self.file_path)}\n\nTiếp tục?"
        ):
            return

        # Start processing in background thread
        self.processing = True
        self.process_btn.configure(text=" Đang xử lý...", state="disabled")

        self.append_output(f"\n{'=' * 60}\n")
        self.append_output(f" 🚀 Bắt đầu xử lý file...\n")
        self.append_output(f" 📁 File: {os.path.basename(self.file_path)}\n")
        self.append_output(f"{'=' * 60}\n\n")

        # Run in thread
        self.process_thread = threading.Thread(target=self.process_file, daemon=True)
        self.process_thread.start()

    def process_file(self):
        """Xử lý file Excel hoặc CSV trong background thread"""
        try:
            # Xác định loại file và đọc dữ liệu
            file_ext = os.path.splitext(self.file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                self.append_output(" 📖 Đang đọc file Excel...\n")
                df = pd.read_excel(self.file_path)
            elif file_ext == '.csv':
                self.append_output(" 📖 Đang đọc file CSV...\n")
                df = pd.read_csv(self.file_path)
            else:
                self.append_output(f" ❌ Định dạng file không được hỗ trợ: {file_ext}\n")
                return

            self.append_output(f" ✅ Đã đọc file thành công!\n")
            self.append_output(f" 📊 Số dòng dữ liệu: {len(df)}\n")
            self.append_output(f" 📋 Số cột: {len(df.columns)}\n\n")

            # Import và gọi hàm xử lý
            from toolsAction.carebaseAction.process_carebase import (
                process_carebase_data,
                save_processed_data,
            )

            # Xử lý dữ liệu
            processed_df = process_carebase_data(df, self.append_output)

            # Hiển thị dialog để chọn nơi lưu file
            self.append_output(" 💾 Đang mở dialog chọn nơi lưu file...\n")
            
            # Tạo tên file mặc định
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            default_filename = f"{base_name}_processed.xlsx"
            
            # Mở dialog chọn nơi lưu file
            output_file = filedialog.asksaveasfilename(
                title="Chọn nơi lưu file kết quả",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*"),
                ],
                initialfile=default_filename,
            )
            
            if not output_file:
                self.append_output(" ⚠️  Đã hủy lưu file.\n")
                return
            
            # Lưu kết quả
            save_processed_data(processed_df, output_file, self.append_output)

            self.append_output("\n" + "=" * 60 + "\n")
            self.append_output(" ✅ HOÀN THÀNH XỬ LÝ!\n")
            self.append_output(f" 📁 File kết quả: {output_file}\n")
            self.append_output("=" * 60 + "\n\n")

        except Exception as e:
            self.append_output(f"\n ❌ Lỗi khi xử lý: {str(e)}\n")
            import traceback
            self.append_output(f" 📋 Chi tiết lỗi:\n{traceback.format_exc()}\n")

        finally:
            # Reset UI state
            self.tab.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """Reset UI về trạng thái ban đầu"""
        self.processing = False
        self.process_btn.configure(text=" Bắt Đầu Xử Lý", state="normal")

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


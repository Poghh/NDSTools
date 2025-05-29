import tkinter as tk
from tkinter import scrolledtext
from tkcalendar import DateEntry
from tkinter import ttk
import json
from tkinter import messagebox
from toolsAction.beActions.select_file import select_file
from toolsAction.beActions.comment_generator import generate_comment
from toolsAction.beActions.create_java_dto_class import generated_dto


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
            frame_input, text="Chưa chọn file", bg="lightgray", width=30)
        self.file_path_label.pack(pady=10)

        tk.Button(frame_input, text="Chọn File Excel",
                  command=lambda: select_file(self)).pack(pady=5)
        tk.Button(frame_input, text="Generate DTO",
                  command=lambda: generated_dto(self)).pack(pady=5)

        # === COMMENT GENERATOR ===
        tk.Label(frame_input, text="-------------------------",
                 bg="lightgray").pack(pady=10)

        tk.Label(frame_input, text="Tạo Comment File", bg="lightgray",
                 font=("Arial", 10, "bold")).pack(pady=5)

        tk.Label(frame_input, text="Tên tác giả:", bg="lightgray").pack()
        self.author_entry = tk.Entry(frame_input, width=25)
        self.author_entry.pack(pady=2)

        tk.Label(frame_input, text="Mã màn hình:", bg="lightgray").pack()
        self.screen_code_entry = tk.Entry(frame_input, width=25)
        self.screen_code_entry.pack(pady=2)

        tk.Label(frame_input, text="Chọn ngày:", bg="lightgray").pack()
        self.date_entry = DateEntry(frame_input, width=22, background='darkblue', foreground='white',
                                    borderwidth=2, date_pattern='yyyy/mm/dd')
        self.date_entry.pack(pady=2)

        tk.Button(frame_input, text="Tạo Comment",
                  command=lambda: generate_comment(self)).pack(pady=10)

        # # === Sinh Unit Test (Dialog) ===
        tk.Button(frame_input, text="Sinh Unit Test (Dialog)",
                  command=self.open_unit_test_dialog).pack(pady=10)

        # === OUTPUT TEXT ===
        self.output_text = scrolledtext.ScrolledText(
            frame_output, wrap=tk.WORD, width=80, height=30)
        self.output_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    def open_unit_test_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("Sinh Unit Test")
        dialog.geometry("800x800")

        # --- Screen Code ---
        tk.Label(dialog, text="Mã màn hình (GUIコード):").pack(pady=(10, 0))
        screen_code_entry = tk.Entry(dialog, width=40)
        screen_code_entry.pack()

        # --- Service Name ---
        tk.Label(dialog, text="Tên service:").pack(pady=(10, 0))
        service_name_entry = tk.Entry(dialog, width=40)
        service_name_entry.pack()

        # --- Endpoint Type ---
        tk.Label(dialog, text="Loại xử lý (select/update):").pack(pady=(10, 0))
        endpoint_var = tk.StringVar(value="select")
        endpoint_menu = ttk.Combobox(dialog, textvariable=endpoint_var, values=[
                                     "select", "update"], state="readonly")
        endpoint_menu.pack()

        # --- Input JSON Header (Label + Beautify Button) ---
        frame_json_header = tk.Frame(dialog)
        # ~5% padding mỗi bên
        frame_json_header.pack(fill=tk.X, padx=40, pady=(20, 0))

        tk.Label(frame_json_header, text="Input JSON:").pack(side=tk.LEFT)

        def beautify_json():
            try:
                raw = json_text.get("1.0", tk.END)
                data = json.loads(raw)
                formatted = json.dumps(data, indent=4, ensure_ascii=False)
                json_text.delete("1.0", tk.END)
                json_text.insert(tk.END, formatted)
            except Exception as e:
                messagebox.showerror(
                    "Lỗi JSON", f"JSON không hợp lệ:\n{str(e)}")

        tk.Button(frame_json_header, text="Validate & Beautify JSON",
                  command=beautify_json).pack(side=tk.RIGHT)

        # --- Input JSON Text Area ---
        frame_json_text = tk.Frame(dialog)
        frame_json_text.pack(fill=tk.BOTH, expand=True, padx=40, pady=5)

        json_text = scrolledtext.ScrolledText(frame_json_text, height=15)
        json_text.pack(fill=tk.BOTH, expand=True)

        # --- Nút Generate ---
        tk.Button(dialog, text="Generate Unit Test Method").pack(pady=5)

        # --- Output Java Code Text Area ---
        frame_output_text = tk.Frame(dialog)
        frame_output_text.pack(fill=tk.BOTH, expand=True,
                               padx=40, pady=(10, 20))

        output_text = scrolledtext.ScrolledText(frame_output_text, height=15)
        output_text.pack(fill=tk.BOTH, expand=True)

from tkinter import filedialog


def select_file(tab_instance):
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        parts = file_path.split("/")
        api_part = next((part for part in parts if part.startswith("API")), None)
        tab_instance.file_path = file_path  # lưu vào biến self
        tab_instance.file_path_label.config(text=api_part)

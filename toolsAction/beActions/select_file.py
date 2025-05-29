from tkinter import filedialog


def select_file(tab_instance):
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        tab_instance.file_path = file_path  # lưu vào biến self
        tab_instance.file_path_label.config(text=file_path)

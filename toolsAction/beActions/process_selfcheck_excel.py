import os
import tkinter as tk

import pandas as pd


def select_self_check_file(self):
    from tkinter import filedialog

    file_path = filedialog.askopenfilename(
        title="Chọn file Self Check (Excel)",
        filetypes=[("Excel files", "*.xlsx *.xls")],
    )
    if file_path:
        process_selfcheck_excel(
            file_path=file_path,
            label_widget=self.self_check_label,
            listbox_widget=self.file_listbox,
            screen_code_entry=self.screen_code_entry,
            author_entry=self.author_entry,
        )


def process_selfcheck_excel(
    file_path: str,
    label_widget: tk.Label,
    listbox_widget: tk.Listbox,
    screen_code_entry: str,
    author_entry: str,
):
    if not file_path:
        label_widget.config(text="❌ Không có file nào được chọn", fg="red")
        listbox_widget.delete(0, tk.END)
        return

    file_name = os.path.basename(file_path)
    label_widget.config(text=f"📁 {file_name}", fg="green")
    listbox_widget.delete(0, tk.END)

    if "_" in file_name and isinstance(screen_code_entry, tk.Entry):
        parts = file_name.split("_")
        if len(parts) >= 3:
            screen_code = parts[1].strip()
            screen_name = parts[2].replace(".xlsx", "").replace(".xls", "").strip()
            full_code = f"{screen_code}_{screen_name}"

            screen_code_entry.delete(0, tk.END)
            screen_code_entry.insert(0, full_code)

    try:
        workbook = pd.read_excel(file_path, sheet_name="機能別ソース一覧", header=None)
    except Exception as e:
        listbox_widget.insert(tk.END, f"❌ Lỗi đọc sheet 機能別ソース一覧: {str(e)}")
        return

    result = []
    name = ""
    for _index, row in workbook.iterrows():
        if (
            pd.notna(row[4])
            and "KMD" in str(row[4])
            and name == ""
            and isinstance(author_entry, tk.Entry)
        ):
            name = str(row[4]).strip()
            author_entry.delete(0, tk.END)
            author_entry.insert(0, name)
        # Cột 3 = 状態 (tình trạng), Cột 2 = ファイルパス (đường dẫn file)
        if str(row[3]).strip() == "新規" and pd.notna(row[2]):
            result.append(str(row[2]).strip())

    if not result:
        listbox_widget.insert(tk.END, "⚠️ Không tìm thấy dòng nào có trạng thái '新規'")
    else:
        for path in result:
            listbox_widget.insert(tk.END, path)

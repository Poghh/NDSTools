import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

def upload_excel(self):
    file_path = filedialog.askopenfilename(
        title="Chọn file Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        self.excel_label.config(text="❌ Không có file nào được chọn", fg="red")
        # Clear the output text area
        self.excel_output.delete("1.0", tk.END)
        return

    file_name = os.path.basename(file_path)
    self.excel_label.config(text=f"📁 {file_name}", fg="green")
    self.excel_output.delete("1.0", tk.END)

    try:
        workbook = pd.read_excel(file_path, sheet_name='項目一覧', header=None)
    except Exception as e:
        self.excel_output.insert(tk.END, f"❌ Lỗi khi đọc sheet 項目一覧: {str(e)}\n")
        return

    result = []
    mark_gui = None

    # Tìm cột chứa "画面No."
    for col_idx, cell in enumerate(workbook.iloc[0]):
        if str(cell).strip() == "画面No.":
            mark_gui = col_idx
            break

    for _, row in workbook.iterrows():
        if len(row) > mark_gui+1:
            code = row[mark_gui+1]
            name = row[mark_gui+1+1] if len(row) > mark_gui+1+1 else ''
            if pd.notna(code) and isinstance(code, str) and 'Or' in code:
                result.append({'code': code.strip(), 'name': str(name).strip()})

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
            self.excel_output.insert(tk.END, f"⚠️ Lỗi khi lấy GUI code/name: {str(e)}\n")

    for item in result:
        if item['code'] not in seen:
            seen.add(item['code'])
            unique_result.append(item)

    for item in unique_result:
        self.excel_output.insert(tk.END, f"🔹 {item['code']} - {item['name']}\n")

def convert_author_to_uppercase(self, *args):
    current = self.author_var.get()
    upper = current.upper()
    if current != upper:
        self.author_var.set(upper) 
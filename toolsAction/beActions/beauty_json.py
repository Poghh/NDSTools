import json
import tkinter as tk
from tkinter import messagebox


def beautify_json(json_text):
    try:
        raw = json_text.get("1.0", tk.END)
        data = json.loads(raw)
        formatted = json.dumps(data, indent=4, ensure_ascii=False)
        json_text.delete("1.0", tk.END)
        json_text.insert(tk.END, formatted)
    except Exception as e:
        messagebox.showerror("Lỗi JSON", f"JSON không hợp lệ:\n{str(e)}")

import os
import re
import tkinter as tk


def check_console_log(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    console_pattern = re.compile(r"console\.(log|warn|error|info|debug|trace)\s*\(")
    results = []

    for file_path in files:
        if not file_path.endswith(".vue"):
            continue
        if not os.path.exists(file_path):
            self.output_text.insert(tk.END, f" Không tìm thấy file: {file_path}\n", "error")
            continue

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            if console_pattern.search(line):
                results.append(
                    (file_path, idx + 1, lines[max(0, idx - 2) : min(len(lines), idx + 3)])
                )

    if not results:
        self.output_text.insert(tk.END, " Không phát hiện console thừa.\n", "success")
    else:
        grouped = {}
        for path, lineno, snippet in results:
            base = os.path.basename(path)
            grouped.setdefault(base, []).append((lineno, snippet))

        for base, items in grouped.items():
            self.output_text.insert(tk.END, f" File {base}:\n", "title-color")
            for lineno, snippet in items:
                self.output_text.insert(
                    tk.END, f"➥ dòng {lineno} chứa console không hợp lệ\n", "error"
                )
                self.output_text.insert(tk.END, "".join(snippet) + "\n")

    self.output_text.insert(tk.END, "\n Kiểm tra console log hoàn tất.\n", "footer-color")
    self.set_running_state(False)

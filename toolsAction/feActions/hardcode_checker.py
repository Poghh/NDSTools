import os
import re
import tkinter as tk


def check_hardcode_jp(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    jp_pattern = re.compile(r"[\u3040-\u30FF\u4E00-\u9FAF]+")
    results = []

    for file_path in files:
        base_name = os.path.basename(file_path)
        if not (file_path.endswith(".vue") and base_name.startswith("Or")):
            continue
        if not os.path.exists(file_path):
            self.output_text.insert(tk.END, f"❌ Không tìm thấy file: {file_path}\n", "error")
            continue

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            code_part = line.split("//")[0].split("/*")[0].split("<!--")[0]
            if jp_pattern.search(code_part):
                stripped_line = line.strip()
                if re.match(r"^\s*(//|/\*|\*|<!--)", stripped_line):
                    continue
                matched_jp = jp_pattern.findall(code_part)
                hardcoded_str = " ".join(matched_jp)
                results.append(
                    (
                        file_path,
                        idx + 1,
                        hardcoded_str,
                        lines[max(0, idx - 2) : min(len(lines), idx + 3)],
                    )
                )

    if not results:
        self.output_text.insert(
            tk.END, "✅ Không phát hiện hardcode tiếng Nhật ngoài comment.\n", "success"
        )
    else:
        grouped = {}
        for path, lineno, jp_text, snippet in results:
            base = os.path.basename(path)
            grouped.setdefault(base, []).append((lineno, jp_text, snippet))

        for base, items in grouped.items():
            self.output_text.insert(tk.END, f"file {base}:\n", "error")
            for lineno, jp_text, snippet in items:
                self.output_text.insert(
                    tk.END, f"dòng {lineno} chứa chuỗi tiếng Nhật hardcode: {jp_text}\n", "error"
                )
                self.output_text.insert(tk.END, "".join(snippet) + "\n")

    self.output_text.insert(tk.END, "\n✅ Kiểm tra hardcode JP hoàn tất.\n")
    self.set_running_state(False)

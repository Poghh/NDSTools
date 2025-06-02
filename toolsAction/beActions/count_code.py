import os
import tkinter as tk


def count_code(listbox_widget, output_widget):
    total_code_lines = 0
    total_comment_lines = 0
    results = []
    current_dir = os.getcwd()

    def count_file_lines(file_path):
        nonlocal total_code_lines, total_comment_lines

        code_lines = 0
        comment_lines = 0
        in_block_comment = False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if in_block_comment:
                        comment_lines += 1
                        if "*/" in line:
                            in_block_comment = False
                        continue

                    if line.startswith("//"):
                        comment_lines += 1
                    elif line.startswith("/*"):
                        comment_lines += 1
                        if "*/" not in line:
                            in_block_comment = True
                    elif "/*" in line:
                        comment_lines += 1
                        code_lines += 1
                        if "*/" not in line:
                            in_block_comment = True
                    else:
                        code_lines += 1

            total_code_lines += code_lines
            total_comment_lines += comment_lines

            results.append(
                f"✅ {file_path}\n  Code: {code_lines}, Comment: {comment_lines}\n"
            )

        except Exception as e:
            results.append(f"❌ {file_path}\n  Error: {str(e)}\n")

    # Duyệt tất cả file trong listbox
    for index in range(listbox_widget.size()):
        relative_path = listbox_widget.get(index).strip()
        if not relative_path:
            continue
        full_path = os.path.join(current_dir, relative_path)
        count_file_lines(full_path)

    # Hiển thị kết quả vào output_widget
    output_widget.delete("1.0", tk.END)
    for line in results:
        output_widget.insert(tk.END, line)
    output_widget.insert(tk.END, "\n==== TOTAL ====\n")
    output_widget.insert(tk.END, f"🧾 Total Code Lines: {total_code_lines}\n")
    output_widget.insert(tk.END, f"📝 Total Comment Lines: {total_comment_lines}\n")

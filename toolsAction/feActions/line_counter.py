import os
import tkinter as tk


def count_lines(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    total_code = 0
    total_comment = 0
    total_blank = 0

    for file_path in files:
        full_path = os.path.abspath(file_path.replace("\\", "/"))
        self.output_text.insert(tk.END, f"\n Đếm dòng: {file_path}\n")
        if not os.path.exists(full_path):
            self.output_text.insert(tk.END, f" Không tìm thấy file: {file_path}\n", "error")
            continue

        try:
            with open(full_path, encoding="utf-8") as f:
                lines = f.readlines()

            code_count = 0
            comment_count = 0
            blank_count = 0

            for line in lines:
                trimmed = line.strip()
                if trimmed.startswith(("//", "/*", "*", "<!--")):
                    comment_count += 1
                elif trimmed == "":
                    blank_count += 1
                else:
                    code_count += 1

            total_code += code_count
            total_comment += comment_count
            total_blank += blank_count
            self.output_text.insert(
                tk.END, f" {code_count} dòng code, {blank_count} dòng trắng, {comment_count} dòng comment\n"
            )

        except Exception as e:
            self.output_text.insert(tk.END, f" Lỗi đọc file: {str(e)}\n", "error")

    self.output_text.insert(
        tk.END, f"\n TỔNG: {total_code} dòng code, {total_blank} dòng trắng, {total_comment} dòng comment\n"
    )
    self.output_text.insert(
        tk.END,
        f"\n TỔNG thêm các file chung: {round(total_code * 1.03)} dòng code, {total_blank} dòng trắng, {round(total_comment * 1.006)} dòng comment\n",
    )
    self.output_text.insert(tk.END, "\n Đếm dòng hoàn tất.\n")
    self.set_running_state(False)

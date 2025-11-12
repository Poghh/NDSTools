import os
import tkinter as tk


def count_code(listbox_widget, output_widget):
    total_code_lines = 0
    total_comment_lines = 0
    total_blank_lines = 0
    results = []
    current_dir = os.getcwd()

    def count_file_lines(file_path):
        nonlocal total_code_lines, total_comment_lines, total_blank_lines

        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        in_block_comment = False

        def handle_inline_block_comment(line_stripped):
            """
            Xử lý trường hợp có /* ... */ nằm trên cùng một dòng (và có thể có code hai bên).
            Trả về (consumed: bool, add_code: int, add_comment: int, in_block_comment_new: bool)
            """
            if "/*" not in line_stripped:
                return False, 0, 0, False

            # Tách bên trái '/*' (có thể là code)
            left, right = line_stripped.split("/*", 1)
            left = left.strip()
            add_code = 1 if left else 0
            add_comment = 1  # dòng này chắc chắn có comment

            if "*/" in right:
                # Block đóng ngay trong dòng này
                after = right.split("*/", 1)[1].strip()
                # Nếu còn code phía sau và không bắt đầu bằng comment, tính thêm 1 dòng code
                if after and not after.startswith("//") and "/*" not in after:
                    add_code += 1
                return True, add_code, add_comment, False
            else:
                # Block chưa đóng -> sang trạng thái in_block_comment
                return True, add_code, add_comment, True

        try:
            with open(file_path, encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.rstrip("\n")
                    stripped = line.strip()

                    # 1) Nếu đang ở trong block comment
                    if in_block_comment:
                        comment_lines += 1
                        if "*/" in stripped:
                            # Kết thúc block comment trong dòng này
                            end_idx = stripped.find("*/")
                            after = stripped[end_idx + 2 :].strip()
                            in_block_comment = False
                            if after:
                                # Nếu sau */ là // -> vẫn là comment, nhưng đã tính comment cho dòng rồi, bỏ qua
                                # Nếu sau */ là code thường -> tính thêm 1 dòng code
                                if not after.startswith("//") and "/*" not in after:
                                    code_lines += 1
                        continue

                    # 2) Không ở trong block comment: xử lý dòng trắng trước
                    if stripped == "":
                        blank_lines += 1
                        continue

                    # 3) Dòng có inline // (sau khi loại trừ block comment)
                    if "//" in stripped and "/*" not in stripped:
                        idx = stripped.find("//")
                        left = stripped[:idx].strip()
                        if left:
                            code_lines += 1  # có code trước //
                        comment_lines += 1  # dòng này có comment //
                        continue

                    # 4) Dòng có /* ... */ trên cùng một dòng hoặc mở block
                    consumed, add_code, add_comment, open_block = handle_inline_block_comment(
                        stripped
                    )
                    if consumed:
                        code_lines += add_code
                        comment_lines += add_comment
                        in_block_comment = open_block
                        continue

                    # 5) Nếu không khớp bất kỳ comment nào -> là dòng code
                    code_lines += 1

            total_code_lines += code_lines
            total_comment_lines += comment_lines
            total_blank_lines += blank_lines

            results.append(
                f" {file_path}\n"
                f"  Code: {code_lines}, Comment: {comment_lines}, Blank: {blank_lines}\n"
            )

        except Exception as e:
            results.append(f" {file_path}\n  Error: {str(e)}\n")

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
    output_widget.insert(tk.END, f"🗒️ Total Comment Lines: {total_comment_lines}\n")
    output_widget.insert(tk.END, f"␣ Total Blank Lines: {total_blank_lines}\n")

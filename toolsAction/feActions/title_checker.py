import os
import tkinter as tk


def check_title_comment(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    author_name = self.author_entry.get().strip()
    if not author_name:
        self.output_text.insert(
            tk.END, " Vui lòng nhập tên tác giả trước khi kiểm tra comment.\n", "error"
        )
        self.set_running_state(False)
        return

    excel_data = self.excel_output.get("1.0", tk.END).strip().splitlines()
    if not excel_data:
        self.output_text.insert(tk.END, " Không tìm thấy dữ liệu từ Excel.\n", "error")
        self.set_running_state(False)
        return

    component_map = {}
    gui_code = ""
    for line in excel_data:
        if line.startswith(""):
            try:
                code, name = line.replace("", "").strip().split(" - ", 1)
                component_map[code] = name
                if code.startswith("GUI"):
                    gui_code = code
            except Exception:
                continue

    gui_name = component_map.get(gui_code)

    for file_path in files:
        file_name = os.path.basename(file_path)
        if not gui_name:
            self.output_text.insert(
                tk.END, f" {file_name}: Không tìm thấy tên màn hình từ Excel\n", "error"
            )

        if file_name.startswith("GUI") and file_name.endswith(".vue"):
            check_gui_file(self, file_path, file_name, gui_code, gui_name, author_name)
        elif file_name.startswith("Or") and file_name.endswith(".vue"):
            check_or_file(
                self, file_path, file_name, gui_code, gui_name, author_name, component_map
            )
        elif file_name.startswith("Or") and file_name.endswith(".constants.ts"):
            check_constants_file(
                self, file_path, file_name, gui_code, gui_name, author_name, component_map
            )
        elif file_name.startswith("Or") and file_name.endswith(".logic.ts"):
            check_logic_file(
                self, file_path, file_name, gui_code, gui_name, author_name, component_map
            )
        elif file_name.startswith("Or") and file_name.endswith(".type.d.ts"):
            check_type_file(
                self, file_path, file_name, gui_code, gui_name, author_name, component_map
            )
        elif file_name.endswith("Type.d.ts"):
            check_type_2_file(
                self, file_path, file_name, gui_code, gui_name, author_name, component_map
            )
        else:
            self.output_text.insert(
                tk.END, f" {file_name}: Không phải file cần kiểm tra\n", "warning"
            )

    self.output_text.insert(tk.END, "\n Kiểm tra hoàn tất.\n")
    self.set_running_state(False)


def check_gui_file(self, file_path, file_name, gui_code, gui_name, author_name):
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        expected = f"""/**
 * {gui_code}_{gui_name}
 *
 * @description
 * {gui_name}
 *
 * @author KMD {author_name}
 */"""

        check_file_content(
            self, file_path, file_name, content, expected, gui_code, gui_name, author_name
        )
    except Exception as e:
        self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_or_file(self, file_path, file_name, gui_code, gui_name, author_name, component_map):
    or_code = file_name.replace(".vue", "")
    if or_code not in component_map:
        self.output_text.insert(
            tk.END, f" {file_name}: Không tìm thấy tên component từ Excel\n", "error"
        )
    else:
        or_name = component_map[or_code]
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            expected = f"""/**
 * {or_code}:{or_name}
 * {gui_code}_{gui_name}
 *
 * @description
 * {or_name}
 *
 * @author KMD {author_name}
 */"""

            check_file_content(
                self,
                file_path,
                file_name,
                content,
                expected,
                gui_code,
                gui_name,
                author_name,
                or_code,
                or_name,
            )
        except Exception as e:
            self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_constants_file(
    self, file_path, file_name, gui_code, gui_name, author_name, component_map
):
    or_code = file_name.replace(".constants.ts", "")
    if or_code not in component_map:
        self.output_text.insert(
            tk.END, f" {file_name}: Không tìm thấy tên component từ Excel\n", "error"
        )
    else:
        or_name = component_map[or_code]
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            expected = f"""/**
 * {or_code}:{or_name}
 * {gui_code}_{gui_name}
 *
 * @description
 * 静的データ
 *
 * @author KMD {author_name}
 */"""

            check_file_content(
                self,
                file_path,
                file_name,
                content,
                expected,
                gui_code,
                gui_name,
                author_name,
                or_code,
                or_name,
                "静的データ",
            )
        except Exception as e:
            self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_logic_file(self, file_path, file_name, gui_code, gui_name, author_name, component_map):
    or_code = file_name.replace(".logic.ts", "")
    if or_code not in component_map:
        self.output_text.insert(
            tk.END, f" {file_name}: Không tìm thấy tên component từ Excel\n", "error"
        )
    else:
        or_name = component_map[or_code]
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            expected = f"""/**
 * {or_code}:{or_name}
 * {gui_code}_{gui_name}
 *
 * @description
 * 処理ロジック
 *
 * @author KMD {author_name}
 */"""

            check_file_content(
                self,
                file_path,
                file_name,
                content,
                expected,
                gui_code,
                gui_name,
                author_name,
                or_code,
                or_name,
                "処理ロジック",
            )
        except Exception as e:
            self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_type_file(self, file_path, file_name, gui_code, gui_name, author_name, component_map):
    or_code = file_name.replace(".type.d.ts", "")
    if or_code not in component_map:
        self.output_text.insert(
            tk.END, f" {file_name}: Không tìm thấy tên component từ Excel\n", "error"
        )
    else:
        or_name = component_map[or_code]
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            expected = f"""/**
 * {or_code}:{or_name}
 * {gui_code}_{gui_name}
 *
 * @description
 * OneWayBind領域用の構造
 *
 * @author KMD {author_name}
 */"""

            check_file_content(
                self,
                file_path,
                file_name,
                content,
                expected,
                gui_code,
                gui_name,
                author_name,
                or_code,
                or_name,
                "OneWayBind領域用の構造",
            )
        except Exception as e:
            self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_type_2_file(self, file_path, file_name, gui_code, gui_name, author_name, component_map):
    or_code = file_name.replace("Type.d.ts", "")
    if or_code not in component_map:
        self.output_text.insert(
            tk.END, f" {file_name}: Không tìm thấy tên component từ Excel\n", "error"
        )
    else:
        or_name = component_map[or_code]
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            expected = f"""/**
 * {or_code}:{or_name}
 * {gui_code}_{gui_name}
 *
 * @description
 * 双方向バインドのデータ構造
 *
 * @author KMD {author_name}
 */"""

            check_file_content(
                self,
                file_path,
                file_name,
                content,
                expected,
                gui_code,
                gui_name,
                author_name,
                or_code,
                or_name,
                "双方向バインドのデータ構造",
            )
        except Exception as e:
            self.output_text.insert(tk.END, f" {file_name}: Lỗi đọc file - {str(e)}\n", "error")


def check_file_content(
    self,
    file_path,
    file_name,
    content,
    expected,
    gui_code,
    gui_name,
    author_name,
    or_code=None,
    or_name=None,
    description=None,
):
    if expected not in content:
        self.output_text.insert(tk.END, f" {file_name}:\n", "error")

        self.output_text.insert(tk.END, " Mong muốn:\n", "highlight")
        self.output_text.insert(tk.END, f"{expected}\n")

        lines12 = content.splitlines()[:12]
        self.output_text.insert(tk.END, " Code:\n", "highlight")
        self.output_text.insert(tk.END, f"{'\n'.join(lines12)}\n")
        self.output_text.insert(tk.END, "\n")
    else:
        self.output_text.insert(tk.END, f" {file_name}: Đúng định dạng\n", "success")

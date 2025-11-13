import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from tkcalendar import DateEntry

from toolsAction.beActions.comment_generator import generate_comment
from toolsAction.beActions.count_code import count_code
from toolsAction.beActions.create_java_dto_class import generated_dto
from toolsAction.beActions.process_selfcheck_excel import (
    process_selfcheck_excel,
    select_self_check_file,
)
from toolsAction.beActions.run_database_initialization import (
    run_database_initialization,
)
from toolsAction.beActions.run_sql_folder import run_sql_from_folder
from toolsAction.beActions.select_file import select_file
from toolsUI.beTab.unit_test_generater_dialog import UnitTestDialog


class BackEndTab:
    def __init__(self, parent):
        self.tab = tk.Frame(parent)
        parent.add(self.tab, text="Back-End")
        self.build_ui()

    def build_ui(self):
        # === Cấu hình bố cục chính cho self.tab ===
        self.tab.columnconfigure(0, weight=1)
        self.tab.columnconfigure(1, weight=3)
        self.tab.rowconfigure(0, weight=1)

        # === FRAME TRÁI ===
        frame_input = tk.Frame(self.tab, bg="lightgray")
        frame_input.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        frame_input.columnconfigure(0, weight=1)

        # === FRAME PHẢI ===
        frame_output = tk.Frame(self.tab)
        frame_output.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame_output.rowconfigure(0, weight=1)
        frame_output.columnconfigure(0, weight=1)

        # === [1] SELF CHECK === (được đưa lên đầu tiên)
        helper_frame = tk.LabelFrame(frame_input, text=" Self Check", bg="lightgray")
        helper_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.self_check_path = None
        self.self_check_label = tk.Label(
            helper_frame, text="Chưa chọn file", bg="lightgray", font=("Arial", 8)
        )
        self.self_check_label.pack(pady=(2, 0), anchor="center")

        tk.Label(
            helper_frame,
            text="— Dán danh sách mã màn hình (mỗi dòng 1 mã) —",
            bg="lightgray",
            font=("Arial", 8, "italic"),
        ).pack(anchor="center", pady=(8, 2))

        paste_frame = tk.Frame(helper_frame, bg="lightgray")
        paste_frame.pack(padx=5, pady=2, fill=tk.BOTH, expand=True)

        # Text để dán list mã
        text_scroller_x = tk.Scrollbar(paste_frame, orient=tk.HORIZONTAL)
        text_scroller_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.screen_codes_text = tk.Text(
            paste_frame, height=6, wrap="none", xscrollcommand=text_scroller_x.set
        )
        self.screen_codes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroller_x.config(command=self.screen_codes_text.xview)

        codes_listbox_frame = tk.Frame(helper_frame)
        codes_listbox_frame.pack(padx=5, pady=2, fill=tk.BOTH, expand=True)

        # nơi giữ danh sách mã để dùng tiếp (nếu cần)
        self.screen_codes = []

        tk.Button(
            helper_frame,
            text="Chọn thư mục Self Check",
            command=self.select_self_check_folder,
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Button(
            helper_frame,
            text="Tải File Self Check",
            command=lambda: select_self_check_file(self),
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Button(
            helper_frame,
            text="Đếm dòng code từ Self Check",
            command=lambda: count_code(self.file_listbox, self.output_text),
        ).pack(pady=2, anchor="center")

        tk.Button(
            helper_frame,
            text="Xuất báo cáo (CSV/Excel)",
            command=self.export_selfcheck_report,
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Label(
            helper_frame,
            text="Danh sách file đã load:",
            bg="lightgray",
            font=("Arial", 8),
        ).pack(anchor="w", padx=5, pady=(5, 0))

        listbox_frame = tk.Frame(helper_frame)
        listbox_frame.pack(padx=5, pady=2, fill=tk.BOTH, expand=True)

        x_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.file_listbox = tk.Listbox(listbox_frame, height=6, xscrollcommand=x_scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        x_scrollbar.config(command=self.file_listbox.xview)

        # === [2] COMMENT & UNIT TEST GENERATOR ===
        comment_frame = tk.LabelFrame(
            frame_input, text="Tạo Comment cho File & Unit Test", bg="lightgray"
        )
        comment_frame.grid(row=1, column=0, sticky="ew", pady=10)

        tk.Label(comment_frame, text="Tên tác giả:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.author_entry = tk.Entry(comment_frame, width=25)
        self.author_entry.pack(pady=2, anchor="center")

        tk.Label(comment_frame, text="Mã màn hình:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.screen_code_entry = tk.Entry(comment_frame, width=25)
        self.screen_code_entry.pack(pady=2, anchor="center")

        tk.Label(comment_frame, text="Chọn ngày:", bg="lightgray").pack(
            anchor="center", pady=(5, 0)
        )
        self.date_entry = DateEntry(
            comment_frame,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy/mm/dd",
            width=22,
        )
        self.date_entry.pack(pady=2, anchor="center")

        tk.Button(
            comment_frame,
            text="Tạo Comment",
            command=lambda: generate_comment(self),
            width=25,
        ).pack(pady=(5, 2), anchor="center")

        tk.Button(
            comment_frame,
            text="Sinh Unit Test (Dialog)",
            command=self.check_and_open_unittest_dialog,
            width=25,
        ).pack(pady=(0, 5), anchor="center")

        # === [3] FILE CHỌN & DTO === (di chuyển xuống cuối)
        file_frame = tk.LabelFrame(frame_input, text="Chọn File & Tạo DTO", bg="lightgray")
        file_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.file_path = None
        self.file_path_label = tk.Label(file_frame, text="Chưa chọn file", bg="lightgray")
        self.file_path_label.pack(pady=5, anchor="center")

        tk.Button(
            file_frame,
            text="Chọn File Excel",
            command=lambda: select_file(self),
            width=25,
        ).pack(pady=2, anchor="center")

        tk.Button(
            file_frame,
            text="Generate DTO",
            command=lambda: generated_dto(self),
            width=25,
        ).pack(pady=2, anchor="center")

        # === [4] NÚT KHỞI TẠO DB ===
        init_db_frame = tk.LabelFrame(frame_input, text="Khởi tạo Cơ sở dữ liệu", bg="lightgray")
        init_db_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        tk.Button(
            init_db_frame,
            text="Khởi tạo DB",
            command=lambda: run_database_initialization(self),
            width=25,
        ).pack(pady=5, anchor="center")

        tk.Button(
            init_db_frame,
            text="Tạo Data từ thư mục SQL",
            command=lambda: run_sql_from_folder(self),
            width=25,
        ).pack(pady=(0, 5), anchor="center")

        # === OUTPUT TEXT ===
        self.output_text = scrolledtext.ScrolledText(frame_output, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew")

    def check_and_open_unittest_dialog(self):
        screen_code = self.screen_code_entry.get().strip()

        if not screen_code:
            messagebox.showwarning(
                "Thiếu thông tin", "Vui lòng nhập đầy đủ Tên tác giả và Mã màn hình."
            )
            return

        UnitTestDialog(self.tab, screen_code=screen_code)

    def select_self_check_folder(self):
        """Chọn thư mục chứa các file Self Check, lọc theo mã GUI trong ô văn bản và xử lý từng file Excel."""
        # 1️⃣ Lấy danh sách mã GUIxxxxx từ vùng văn bản
        raw = self.screen_codes_text.get("1.0", tk.END)
        found = re.findall(
            r"(?<![A-Za-z0-9])(GUI\d{5}|[A-Z][A-Z0-9]{5})(?![A-Za-z0-9])", raw, flags=re.IGNORECASE
        )

        seen = set()
        self.screen_codes = []
        for c in (x.upper().strip() for x in found):
            if c and c not in seen:
                seen.add(c)
                self.screen_codes.append(c)

        if not self.screen_codes:
            messagebox.showinfo(
                "Chưa có danh sách mã",
                "Vui lòng dán danh sách mã (mỗi dòng 1 mã) vào ô phía trên trước khi chọn thư mục.",
            )
            return

        # 2️⃣ Chọn thư mục chứa file self-check
        folder_path = filedialog.askdirectory(title="Chọn thư mục Self Check")
        if not folder_path:
            return

        self.self_check_path = folder_path
        self.self_check_label.config(text=f"Thư mục: {os.path.basename(folder_path)}")

        # 3️⃣ Lấy danh sách file Excel trong thư mục
        valid_exts = (".xlsx", ".xls", ".xlsm", ".csv")
        all_files = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(valid_exts)
        ]
        if not all_files:
            messagebox.showwarning(
                "Không có file",
                "Không tìm thấy file Self Check (.xlsx/.xls/.xlsm/.csv) trong thư mục này.",
            )
            return

        # 4️⃣ Lọc file có chứa mã
        matched_files = []
        for f in all_files:
            fu = f.upper()
            if any(code in fu for code in self.screen_codes):
                matched_files.append(os.path.join(folder_path, f))

        if not matched_files:
            messagebox.showwarning(
                "Không tìm thấy", "Không có file nào trùng với mã màn hình đã dán."
            )
            return

        # 5️⃣ Lưu danh sách vào biến instance
        self.self_check_files = matched_files

        # 6️⃣ Clear listbox (danh sách file .java sẽ được append từ nhiều file self-check)
        self.file_listbox.delete(0, tk.END)

        # 7️⃣ Gọi process_selfcheck_excel cho từng file self-check
        for path in self.self_check_files:
            try:
                process_selfcheck_excel(
                    file_path=path,
                    label_widget=self.self_check_label,
                    listbox_widget=self.file_listbox,
                    screen_code_entry=self.screen_code_entry,
                    author_entry=self.author_entry,
                    clear_listbox=False,  # rất quan trọng: giữ lại các file đã add trước đó
                )
            except Exception as e:
                self.output_text.insert(
                    tk.END, f"\n⚠️ Lỗi khi xử lý {os.path.basename(path)}: {e}\n"
                )

        # 8️⃣ Sau khi đã có đầy đủ danh sách file .java trong listbox, gọi count_code
        try:
            total_code, total_blank, total_comment = count_code(
                listbox_widget=self.file_listbox,
                output_widget=self.output_text,
            )
            # (count_code đã tự xóa nội dung output_widget trước khi ghi)
            self.output_text.insert(
                tk.END,
                f"\n==== SUMMARY FROM FOLDER ====\n"
                f"📂 Thư mục: {folder_path}\n"
                f"🧾 Code: {total_code}, ␣ Blank: {total_blank}, 🗒️ Comment: {total_comment}\n",
            )
        except Exception as e:
            self.output_text.insert(
                tk.END,
                f"\n⚠️ Lỗi khi đếm dòng code từ danh sách file: {e}\n",
            )

    def export_selfcheck_report(self):
        if not getattr(self, "self_check_files", None):
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Chưa có danh sách file self-check. Hãy chọn thư mục Self Check trước.",
            )
            return

        rows = []
        for sc_path in self.self_check_files:
            base = os.path.basename(sc_path)

            # trích mã màn hình từ tên file
            screen = ""
            parts = base.split("_")
            for p in parts:
                up = p.upper()
                if up.startswith("GUI") and len(up) >= 8 and up[3:8].isdigit():
                    screen = up[:8]  # GUI + 5 số
                    break

            # 🔹 Lấy danh sách source .java 状態=新規 bằng process_selfcheck_excel
            sources = process_selfcheck_excel(
                file_path=sc_path,
                label_widget=self.self_check_label,  # hoặc 1 label khác nếu bạn muốn
                listbox_widget=self.file_listbox,  # có thể là listbox UI thật
                screen_code_entry=self.screen_code_entry,
                author_entry=self.author_entry,
                clear_listbox=False,  # rất quan trọng: không xóa listbox UI
            )

            if not sources:
                # Không có file .java 新規 → vẫn ghi dòng với 0
                rows.append(
                    {
                        "Màn hình": screen,
                        "File self-check": base,
                        "Số file": 0,
                        "Dòng code": 0,
                        "Dòng trắng": 0,
                        "Dòng comment": 0,
                    }
                )
                continue

            # 🔹 Tạo Listbox tạm chỉ để feed count_code
            temp_listbox = tk.Listbox()
            for src in sources:
                temp_listbox.insert(tk.END, src)

            # 🔹 Text tạm – không gán parent để tránh attribute error
            temp_output = tk.Text()

            # Sử dụng count_code
            total_code, total_blank, total_comment = count_code(
                listbox_widget=temp_listbox,
                output_widget=temp_output,
            )

            rows.append(
                {
                    "Màn hình": screen,
                    "File self-check": base,
                    "Số file": len(sources),
                    "Dòng code": total_code,
                    "Dòng trắng": total_blank,
                    "Dòng comment": total_comment,
                }
            )

        if not rows:
            messagebox.showwarning("Không có dữ liệu", "Không tạo được dòng nào để xuất.")
            return

        df = pd.DataFrame(
            rows,
            columns=[
                "Màn hình",
                "File self-check",
                "Số file",
                "Dòng code",
                "Dòng trắng",
                "Dòng comment",
            ],
        )

        save_path = filedialog.asksaveasfilename(
            title="Lưu báo cáo",
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile="selfcheck_report.xlsx",
        )
        if not save_path:
            return

        df.to_excel(save_path, index=False)
        self._style_xlsx(save_path, df)

        messagebox.showinfo("Hoàn tất", f"Đã xuất báo cáo: {save_path}")

    def _style_xlsx(self, path_xlsx: str, df: pd.DataFrame):
        """Định dạng file .xlsx: header đậm, auto-filter, freeze, căn lề, #,##0, auto-width."""

        wb = load_workbook(path_xlsx)
        ws = wb.active

        # Freeze header + AutoFilter
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        # Style header
        header_font = Font(bold=True)
        header_align = Alignment(horizontal="center", vertical="center")
        header_fill = PatternFill("solid", fgColor="DDDDDD")
        thin = Side(style="thin", color="CCCCCC")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for cell in ws[1]:
            cell.font = header_font
            cell.alignment = header_align
            cell.fill = header_fill
            cell.border = border

        # Căn lề & định dạng số cho các cột số
        num_cols = {"Số file", "Dòng code", "Dòng trắng", "Dòng comment"}
        {c: i + 1 for i, c in enumerate(df.columns)}

        for r in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in r:
                # viền mảnh nhẹ
                cell.border = border

                # nếu là cột số -> #,##0 và căn phải; còn lại căn trái
                col_header = ws.cell(row=1, column=cell.column).value
                if col_header in num_cols:
                    cell.number_format = "#,##0"
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        # Auto width theo nội dung (giới hạn tối đa để không quá rộng)
        max_width = 80
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            header_text = str(ws.cell(row=1, column=col_idx).value or "")
            width = len(header_text) + 2

            for row_idx in range(2, ws.max_row + 1):
                v = ws.cell(row=row_idx, column=col_idx).value
                if v is None:
                    continue
                s = f"{v}"
                # cột số thường không cần quá dài
                if header_text in num_cols:
                    width = max(width, len(s))
                else:
                    width = max(width, len(s))

            ws.column_dimensions[col_letter].width = min(width + 2, max_width)

        wb.save(path_xlsx)

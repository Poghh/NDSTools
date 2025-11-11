import os
from tkinter import filedialog

import pymysql

from toolsAction.beActions.db_config import DB_CONFIG


def run_sql_from_folder(self):
    folder = filedialog.askdirectory(title="Chọn thư mục chứa file .sql")
    if not folder:
        return

    self.output_text.insert("end", f" Đã chọn thư mục: {folder}\n")
    self.output_text.see("end")
    self.tab.update()

    try:
        conn = pymysql.connect(**DB_CONFIG)
        sql_files = sorted([f for f in os.listdir(folder) if f.endswith(".sql")])

        if not sql_files:
            self.output_text.insert("end", " Không tìm thấy file .sql nào trong thư mục.\n")
            return

        for filename in sql_files:
            path = os.path.join(folder, filename)
            try:
                with open(path, encoding="utf-8") as f:
                    sql_content = f.read()

                with conn.cursor() as cur:
                    for statement in sql_content.split(";"):
                        if statement.strip():
                            cur.execute(statement)

                self.output_text.insert("end", f" Success: {filename}\n")
            except Exception as e:
                self.output_text.insert("end", f" Error in {filename}: {e}\n")

        conn.close()
        self.output_text.insert("end", "🎉 Đã xử lý xong toàn bộ file SQL.\n")
    except Exception as e:
        self.output_text.insert("end", f" Lỗi kết nối DB: {e}\n")

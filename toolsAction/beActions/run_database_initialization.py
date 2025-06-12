import os
import re
import subprocess
import sys
from tkinter import messagebox

import pymysql

from toolsAction.beActions.db_config import DB_CONFIG

# --- Định nghĩa đường dẫn thực tế ---
if getattr(sys, "frozen", False):
    # Khi chạy từ file .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Khi chạy từ mã nguồn Python
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_FOLDER_PATH = os.path.join(BASE_DIR, "db")


def run_database_initialization(self):
    """Hàm chính để gọi từ GUI - self là class BackEndTab"""
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn khởi tạo lại cơ sở dữ liệu?")
    if not confirm:
        return

    _log(self, "🚀 Bắt đầu khởi tạo cơ sở dữ liệu...\n")

    try:
        latest_sql_file = find_latest_dump_file()
        run_sql_dump_with_cli(latest_sql_file, lambda msg: _log(self, msg))
        run_additional_sql_commands(lambda msg: _log(self, msg))
        _log(self, "🎉 Khởi tạo DB hoàn tất!\n")
    except Exception as e:
        _log(self, f"❌ Đã xảy ra lỗi: {str(e)}\n")


def _log(self, msg):
    self.output_text.insert("end", msg + "\n")
    self.output_text.see("end")
    self.tab.update()


def find_latest_dump_file():
    """Tìm file Dump*.sql mới nhất trong cùng thư mục chạy (BASE_DIR)."""
    dump_files = [f for f in os.listdir(BASE_DIR) if re.match(r"Dump\d+\.sql$", f)]

    if not dump_files:
        raise FileNotFoundError(
            "❌ Không tìm thấy file dump nào có dạng Dump*.sql trong thư mục hiện tại."
        )

    latest_file = sorted(dump_files)[-1]
    return os.path.join(BASE_DIR, latest_file)


def run_sql_dump_with_cli(dump_file_path, output_callback=print):
    """Chạy file dump bằng pymysql thay vì mysql CLI."""
    output_callback(f"▶ Đang chạy dump file bằng pymysql: {dump_file_path}")

    try:
        conn = pymysql.connect(**DB_CONFIG)
        with open(dump_file_path, encoding="utf-8") as f:
            sql_content = f.read()

        with conn.cursor() as cur:
            for statement in sql_content.split(";"):
                if statement.strip():
                    cur.execute(statement)

        conn.commit()
        conn.close()
        output_callback("✅ Dump file chạy thành công.")
    except Exception as e:
        raise RuntimeError(f"❌ Lỗi khi chạy dump file bằng pymysql:\n{e}") from e


def run_additional_sql_commands(output_callback=print):
    """Chạy các lệnh SQL bổ sung theo yêu cầu."""
    output_callback("▶ Đang xử lý bước chạy lệnh SQL bổ sung trong thư mục /db ...")

    if not os.path.isdir(DB_FOLDER_PATH):
        raise FileNotFoundError(f"❌ Không tìm thấy thư mục db tại: {DB_FOLDER_PATH}")

    # 1. SET GLOBAL sql_mode
    sql_mode_cmd = (
        f"mysql -h {DB_CONFIG['host']} -P {DB_CONFIG['port']} -u root -ppass! "
        f"-D {DB_CONFIG['database']} "
        f"-e \"SET GLOBAL sql_mode = (SELECT IF(LOCATE('NO_AUTO_VALUE_ON_ZERO', @@global.sql_mode) = 0, CONCAT(@@global.sql_mode, ',NO_AUTO_VALUE_ON_ZERO'), @@global.sql_mode));\""
    )
    subprocess.run(sql_mode_cmd, shell=True, check=True)
    output_callback("✔ Đã cập nhật sql_mode")

    # 2. Import ddl_all.sql
    ddl_path = os.path.join(DB_FOLDER_PATH, "ddl_all.sql")
    if not os.path.isfile(ddl_path):
        raise FileNotFoundError("❌ Không tìm thấy ddl_all.sql")

    ddl_cmd = (
        f"mysql -h {DB_CONFIG['host']} -P {DB_CONFIG['port']} -u root -ppass! "
        f'-D {DB_CONFIG["database"]} < "{ddl_path}"'
    )
    subprocess.run(ddl_cmd, shell=True, check=True)
    output_callback("✔ Đã import ddl_all.sql")

    # 3. Import dml_all.sql
    dml_path = os.path.join(DB_FOLDER_PATH, "dml_all.sql")
    if not os.path.isfile(dml_path):
        raise FileNotFoundError("❌ Không tìm thấy dml_all.sql")

    dml_cmd = (
        f"mysql -h {DB_CONFIG['host']} -P {DB_CONFIG['port']} -u devuser -p devuser "
        f'-D {DB_CONFIG["database"]} < "{dml_path}"'
    )
    subprocess.run(dml_cmd, shell=True, check=True)
    output_callback("✔ Đã import dml_all.sql")

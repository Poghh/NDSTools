import os
import re
import subprocess
from tkinter import messagebox

from toolsAction.beActions.db_config import DB_CONFIG

# --- Đường dẫn thư mục ---
WORKSPACE_PATH = "/workspace"
SQL_SCRIPT_PATH = os.path.join(WORKSPACE_PATH, "setup/sql_script")
DB_FOLDER_PATH = os.path.join(WORKSPACE_PATH, "db")

# --- Danh sách lệnh shell khởi tạo ---
INIT_COMMANDS = [
    "sh setup/sql_script/db_initialization.sh",
    "sh setup/sql_script/db_initialization_cphn.sh",
    "sh setup/sql_script/db_initialization_cnf.sh",
]


def run_database_initialization(self):
    """Hàm chính để gọi từ GUI - self là class BackEndTab"""
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn khởi tạo lại cơ sở dữ liệu?")
    if not confirm:
        return

    _log(self, "🚀 Bắt đầu khởi tạo cơ sở dữ liệu...\n")

    try:
        run_shell_scripts(lambda msg: _log(self, msg))
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


def run_shell_scripts(output_callback=print):
    """Chạy các script shell khởi tạo DB."""
    os.chdir(WORKSPACE_PATH)
    for cmd in INIT_COMMANDS:
        output_callback(f"▶ Đang chạy: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        output_callback(f"✔ Thành công:\n{result.stdout}")


def find_latest_dump_file():
    """Tìm file Dump*.sql mới nhất trong cùng thư mục với script này."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dump_files = [f for f in os.listdir(current_dir) if re.match(r"Dump\d+\.sql$", f)]

    if not dump_files:
        raise FileNotFoundError(
            "❌ Không tìm thấy file dump nào có dạng Dump*.sql trong thư mục hiện tại."
        )

    latest_file = sorted(dump_files)[-1]
    return os.path.join(current_dir, latest_file)


def run_sql_dump_with_cli(dump_file_path, output_callback=print):
    """Chạy file dump bằng mysql CLI."""
    mysql_cmd = (
        f"mysql -h {DB_CONFIG['host']} "
        f"-P {DB_CONFIG['port']} "
        f"-u {DB_CONFIG['user']} "
        f"-p{DB_CONFIG['password']} "
        f'{DB_CONFIG["database"]} < "{dump_file_path}"'
    )
    output_callback(f"▶ Đang chạy dump file bằng mysql CLI: {dump_file_path}")
    result = subprocess.run(mysql_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"❌ Lỗi khi chạy dump file:\n{result.stderr}")

    output_callback("✅ Dump file chạy thành công.")


def run_additional_sql_commands(output_callback=print):
    """Chạy các lệnh SQL bổ sung theo yêu cầu."""
    output_callback("▶ Đang xử lý bước chạy lệnh SQL bổ sung trong thư mục /workspace/db ...")

    if not os.path.isdir(DB_FOLDER_PATH):
        raise FileNotFoundError("❌ Không tìm thấy thư mục /workspace/db")

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
        f"mysql -h {DB_CONFIG['host']} -P {DB_CONFIG['port']} -u devuser -pdevuser "
        f'-D {DB_CONFIG["database"]} < "{dml_path}"'
    )
    subprocess.run(dml_cmd, shell=True, check=True)
    output_callback("✔ Đã import dml_all.sql")

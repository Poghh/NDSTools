import os
import re
from typing import Dict, List, Optional, Tuple


def extract_file_info(file_path: str) -> Dict[str, str]:
    """
    Extract basic information from a file

    Args:
        file_path (str): Path to the file

    Returns:
        Dict containing file information
    """
    try:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)

        return {
            "name": file_name,
            "extension": file_ext,
            "size": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "path": file_path,
        }
    except Exception as e:
        return {"error": str(e)}


def is_test_file(file_path: str) -> bool:
    """
    Check if a file is likely a test file based on naming conventions

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if likely a test file
    """
    file_name = os.path.basename(file_path).lower()

    test_patterns = [r".*test.*", r".*spec.*", r".*unittest.*", r".*testcase.*"]

    return any(re.match(pattern, file_name) for pattern in test_patterns)


def get_supported_test_extensions() -> List[str]:
    """Get list of supported test file extensions"""
    return [".java", ".py", ".js", ".ts", ".txt"]


def get_supported_doc_extensions() -> List[str]:
    """Get list of supported documentation file extensions"""
    return [".xlsx", ".xls", ".docx", ".doc", ".pdf", ".txt"]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024, 1)} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{round(size_bytes / (1024 * 1024), 1)} MB"
    else:
        return f"{round(size_bytes / (1024 * 1024 * 1024), 1)} GB"


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate if file path exists and is accessible

    Args:
        file_path (str): Path to validate

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if not file_path:
            return False, "Đường dẫn file trống"

        if not os.path.exists(file_path):
            return False, "File không tồn tại"

        if not os.path.isfile(file_path):
            return False, "Đường dẫn không phải là file"

        if not os.access(file_path, os.R_OK):
            return False, "Không có quyền đọc file"

        return True, "File hợp lệ"

    except Exception as e:
        return False, f"Lỗi kiểm tra file: {str(e)}"


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename for the original file

    Args:
        original_path (str): Original file path

    Returns:
        str: Backup file path
    """
    dir_name = os.path.dirname(original_path)
    file_name = os.path.basename(original_path)
    name, ext = os.path.splitext(file_name)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"{name}_backup_{timestamp}{ext}"
    return os.path.join(dir_name, backup_name)


def safe_read_file(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Safely read file content with error handling

    Args:
        file_path (str): Path to the file
        encoding (str): File encoding, defaults to utf-8

    Returns:
        str: File content or None if error
    """
    try:
        with open(file_path, encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encodings
        encodings = ["utf-8", "cp1252", "iso-8859-1"]
        for enc in encodings:
            try:
                with open(file_path, encoding=enc) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        return None
    except Exception:
        return None

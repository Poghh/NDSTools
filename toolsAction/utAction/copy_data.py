import os
import tkinter as tk
from tkinter import messagebox
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Border, Side
from copy import copy


def copy_data_action(test_file_path, doc_file_path, progress_callback=None):
    """
    Copy data from 項目一覧 sheet in mocks file to 項目一覧 sheet in unit test file
    
    Args:
        test_file_path (str): Path to the mocks file (source)
        doc_file_path (str): Path to the unit test file (destination)
        progress_callback (function): Optional callback to report progress
        
    Returns:
        dict: Result information
    """
    try:
        if progress_callback:
            progress_callback("Đang kiểm tra file...")
        
        # Validate files exist
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Không tìm thấy file mocks: {test_file_path}")
        
        if not os.path.exists(doc_file_path):
            raise FileNotFoundError(f"Không tìm thấy file unit test: {doc_file_path}")
        
        # Check if both files are Excel files
        test_ext = os.path.splitext(test_file_path)[1].lower()
        doc_ext = os.path.splitext(doc_file_path)[1].lower()
        
        if test_ext not in ['.xlsx', '.xls'] or doc_ext not in ['.xlsx', '.xls']:
            raise ValueError("Cả hai file phải là file Excel (.xlsx hoặc .xls)")
        
        if progress_callback:
            progress_callback("Đang đọc file mocks...")
        
        # Load the mocks file (source)
        source_wb = load_workbook(test_file_path, data_only=True)
        
        # Find the 項目一覧 sheet in mocks file
        sheet_name = "項目一覧"
        if sheet_name not in source_wb.sheetnames:
            raise ValueError(f"Không tìm thấy sheet '{sheet_name}' trong file mocks")
        
        source_ws = source_wb[sheet_name]
        
        if progress_callback:
            progress_callback("Đang đọc dữ liệu từ sheet 項目一覧...")
        
        # Get all cells with data and formatting from source sheet (starting from row 5)
        max_row = source_ws.max_row
        max_col = source_ws.max_column
        start_source_row = 5  # Copy from row 5 onwards
        
        # Store source cells for copying with formatting (from row 5)
        source_cells = []
        for row in range(start_source_row, max_row + 1):
            row_cells = []
            for col in range(1, max_col + 1):
                source_cell = source_ws.cell(row=row, column=col)
                row_cells.append(source_cell)
            source_cells.append(row_cells)
        
        if progress_callback:
            progress_callback("Đang mở file unit test...")
        
        # Load the unit test file (destination)
        dest_wb = load_workbook(doc_file_path)
        
        # Find or create the 項目一覧 sheet in unit test file
        if sheet_name not in dest_wb.sheetnames:
            dest_ws = dest_wb.create_sheet(sheet_name)
        else:
            dest_ws = dest_wb[sheet_name]
        
        if progress_callback:
            progress_callback("Đang sao chép dữ liệu và formatting...")
        
        # Paste data starting from row 6 with full formatting
        start_row = 6
        
        # Copy merged cell ranges information first
        merged_ranges = []
        for merged_range in source_ws.merged_cells.ranges:
            # Calculate the offset for the merged range in destination
            min_row = merged_range.min_row
            max_row = merged_range.max_row
            min_col = merged_range.min_col
            max_col = merged_range.max_col
            
            # Only include merged ranges that are within our copying area (from row 5 onwards)
            if min_row >= start_source_row:
                new_min_row = start_row + (min_row - start_source_row)
                new_max_row = start_row + (max_row - start_source_row)
                merged_ranges.append((new_min_row, new_max_row, min_col, max_col))
        
        # Copy cell data and formatting
        for row_idx, row_cells in enumerate(source_cells):
            for col_idx, source_cell in enumerate(row_cells):
                dest_cell = dest_ws.cell(
                    row=start_row + row_idx, 
                    column=col_idx + 1
                )
                
                # Copy cell value
                dest_cell.value = source_cell.value
                
                # Copy cell formatting if source cell has formatting
                if source_cell.has_style:
                    dest_cell.font = copy(source_cell.font)
                    dest_cell.border = copy(source_cell.border)
                    dest_cell.fill = copy(source_cell.fill)
                    dest_cell.number_format = source_cell.number_format
                    dest_cell.protection = copy(source_cell.protection)
                    dest_cell.alignment = copy(source_cell.alignment)
        
        # Apply merged cell ranges to destination
        for new_min_row, new_max_row, min_col, max_col in merged_ranges:
            try:
                dest_ws.merge_cells(
                    start_row=new_min_row,
                    start_column=min_col,
                    end_row=new_max_row,
                    end_column=max_col
                )
            except Exception as e:
                print(f"Warning: Could not merge cells {new_min_row}:{min_col} to {new_max_row}:{max_col} - {e}")

        if progress_callback:
            progress_callback("Đang thêm border và text bổ sung...")
        
        # Add outside border around the copied data
        if source_cells:
            # Define border style
            thin_border = Side(style='thin', color='000000')
            border_style = Border(
                left=thin_border,
                right=thin_border,
                top=thin_border,
                bottom=thin_border
            )
            
            # Calculate the range of copied data
            end_row = start_row + len(source_cells) - 1
            end_col = max_col
            
            # Apply border to the outer cells
            # Top border
            for col in range(1, end_col + 1):
                cell = dest_ws.cell(row=start_row, column=col)
                new_border = Border(
                    top=thin_border,
                    left=cell.border.left,
                    right=cell.border.right,
                    bottom=cell.border.bottom
                )
                if col == 1:  # Left-most cell
                    new_border = Border(
                        top=thin_border,
                        left=thin_border,
                        right=cell.border.right,
                        bottom=cell.border.bottom
                    )
                if col == end_col:  # Right-most cell
                    new_border = Border(
                        top=thin_border,
                        left=cell.border.left,
                        right=thin_border,
                        bottom=cell.border.bottom
                    )
                cell.border = new_border
            
            # Bottom border
            for col in range(1, end_col + 1):
                cell = dest_ws.cell(row=end_row, column=col)
                new_border = Border(
                    bottom=thin_border,
                    left=cell.border.left,
                    right=cell.border.right,
                    top=cell.border.top
                )
                if col == 1:  # Left-most cell
                    new_border = Border(
                        bottom=thin_border,
                        left=thin_border,
                        right=cell.border.right,
                        top=cell.border.top
                    )
                if col == end_col:  # Right-most cell
                    new_border = Border(
                        bottom=thin_border,
                        left=cell.border.left,
                        right=thin_border,
                        top=cell.border.top
                    )
                cell.border = new_border
            
            # Left border
            for row in range(start_row, end_row + 1):
                cell = dest_ws.cell(row=row, column=1)
                new_border = Border(
                    left=thin_border,
                    right=cell.border.right,
                    top=cell.border.top,
                    bottom=cell.border.bottom
                )
                cell.border = new_border
            
            # Right border
            for row in range(start_row, end_row + 1):
                cell = dest_ws.cell(row=row, column=end_col)
                new_border = Border(
                    right=thin_border,
                    left=cell.border.left,
                    top=cell.border.top,
                    bottom=cell.border.bottom
                )
                cell.border = new_border
            
            # Copy data from "data_1" sheet to the next column after the last copied column, starting from row 5
            data_1_sheet_name = "data_1"
            if data_1_sheet_name in dest_wb.sheetnames:
                if progress_callback:
                    progress_callback("Đang copy dữ liệu từ sheet data_1...")
                
                data_1_ws = dest_wb[data_1_sheet_name]
                data_1_max_row = data_1_ws.max_row
                data_1_max_col = data_1_ws.max_column
                
                # Copy all data from data_1 sheet with formatting
                paste_start_col = end_col + 1
                paste_start_row = 5
                
                # Copy merged cell ranges from data_1 sheet
                data_1_merged_ranges = []
                for merged_range in data_1_ws.merged_cells.ranges:
                    min_row = merged_range.min_row
                    max_row = merged_range.max_row
                    min_col = merged_range.min_col
                    max_col = merged_range.max_col
                    
                    # Calculate new position in destination
                    new_min_row = paste_start_row + min_row - 1
                    new_max_row = paste_start_row + max_row - 1
                    new_min_col = paste_start_col + min_col - 1
                    new_max_col = paste_start_col + max_col - 1
                    data_1_merged_ranges.append((new_min_row, new_max_row, new_min_col, new_max_col))
                
                # Copy cell data and formatting
                for row in range(1, data_1_max_row + 1):
                    for col in range(1, data_1_max_col + 1):
                        source_cell = data_1_ws.cell(row=row, column=col)
                        dest_cell = dest_ws.cell(
                            row=paste_start_row + row - 1,
                            column=paste_start_col + col - 1
                        )
                        
                        # Copy cell value
                        dest_cell.value = source_cell.value
                        
                        # Copy cell formatting if source cell has formatting
                        if source_cell.has_style:
                            dest_cell.font = copy(source_cell.font)
                            dest_cell.border = copy(source_cell.border)
                            dest_cell.fill = copy(source_cell.fill)
                            dest_cell.number_format = source_cell.number_format
                            dest_cell.protection = copy(source_cell.protection)
                            dest_cell.alignment = copy(source_cell.alignment)
                
                # Apply merged cell ranges for data_1
                for new_min_row, new_max_row, new_min_col, new_max_col in data_1_merged_ranges:
                    try:
                        dest_ws.merge_cells(
                            start_row=new_min_row,
                            start_column=new_min_col,
                            end_row=new_max_row,
                            end_column=new_max_col
                        )
                    except Exception as e:
                        print(f"Warning: Could not merge data_1 cells {new_min_row}:{new_min_col} to {new_max_row}:{new_max_col} - {e}")
                
                # Add table borders below data_1 section
                if progress_callback:
                    progress_callback("Đang thêm border cho bảng dưới data_1...")
                
                # Calculate table dimensions
                table_start_row = 9  # Fixed start row
                table_end_row = start_row + len(source_cells) - 1  # Last row of mocks data
                table_start_col = paste_start_col  # First column after mocks data
                table_end_col = paste_start_col + data_1_max_col - 1  # Last column of data_1
                
                # Create thin border for the table area
                table_border = Side(style='thin', color='000000')
                
                # Add borders to all cells in the table area
                for row in range(table_start_row, table_end_row + 1):
                    for col in range(table_start_col, table_end_col + 1):
                        cell = dest_ws.cell(row=row, column=col)
                        
                        # Add thin borders to all sides of every cell to create a grid
                        new_border = Border(
                            top=table_border,
                            bottom=table_border,
                            left=table_border,
                            right=table_border
                        )
                        cell.border = new_border
                
                # Delete data_1 sheet after copying its data
                if progress_callback:
                    progress_callback("Đang xóa sheet data_1...")
                
                try:
                    dest_wb.remove(data_1_ws)
                except Exception as e:
                    print(f"Warning: Could not delete data_1 sheet - {e}")
            else:
                # Fallback: Add "Update sau" text if data_1 sheet doesn't exist
                update_cell = dest_ws.cell(row=5, column=end_col + 1)
                update_cell.value = "Update sau"
        
        if progress_callback:
            progress_callback("Đang lưu file...")
        
        # Save the destination file
        dest_wb.save(doc_file_path)
        
        # Close workbooks
        source_wb.close()
        dest_wb.close()
        
        result = {
            "test_file": os.path.basename(test_file_path),
            "doc_file": os.path.basename(doc_file_path),
            "sheet_name": sheet_name,
            "rows_copied": len(source_cells),
            "cols_copied": max_col if source_cells else 0,
            "source_start_row": start_source_row,
            "paste_start_row": start_row,
            "has_border": True,
            "data_1_copied": data_1_sheet_name in dest_wb.sheetnames if source_cells else False,
            "data_1_start_col": max_col + 1 if source_cells else 0,
            "data_1_start_row": 5,
            "data_1_sheet_deleted": True,
            "table_borders_added": True,
            "table_start_row": 9,
            "table_end_row": start_row + len(source_cells) - 1 if source_cells else 0,
            "status": "success"
        }
        
        if progress_callback:
            progress_callback("Hoàn thành!")
        
        return result
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"Lỗi: {str(e)}")
        raise e


def validate_file_compatibility(test_file_path, doc_file_path):
    """
    Check if the uploaded files are compatible for data copying
    
    Args:
        test_file_path (str): Path to test file
        doc_file_path (str): Path to documentation file
        
    Returns:
        dict: Validation result with status and message
    """
    try:
        test_ext = os.path.splitext(test_file_path)[1].lower()
        doc_ext = os.path.splitext(doc_file_path)[1].lower()
        
        # Define supported combinations
        supported_combinations = [
            # Excel to Excel combinations
            ('.xlsx', '.xlsx'), ('.xlsx', '.xls'),
            ('.xls', '.xlsx'), ('.xls', '.xls'),
            # Test file types that can work with Excel docs
            ('.java', '.xlsx'), ('.java', '.xls'),
            ('.py', '.xlsx'), ('.py', '.xls'),
            ('.js', '.xlsx'), ('.js', '.xls'),
            ('.ts', '.xlsx'), ('.ts', '.xls'),
            # Test file types that can work with Word docs  
            ('.java', '.docx'), ('.java', '.doc'),
            ('.py', '.docx'), ('.py', '.doc'),
            # Excel can work with Word docs
            ('.xlsx', '.docx'), ('.xlsx', '.doc'),
            ('.xls', '.docx'), ('.xls', '.doc'),
            # Word can work with Excel docs
            ('.docx', '.xlsx'), ('.docx', '.xls'),
            ('.doc', '.xlsx'), ('.doc', '.xls'),
            # Text files can work with any documentation
            ('.txt', '.xlsx'), ('.txt', '.xls'),
            ('.txt', '.docx'), ('.txt', '.doc'),
            ('.txt', '.txt')
        ]
        
        if (test_ext, doc_ext) in supported_combinations:
            return {
                "compatible": True,
                "message": f"File {test_ext} và {doc_ext} tương thích!"
            }
        else:
            return {
                "compatible": False,
                "message": f"File {test_ext} và {doc_ext} chưa được hỗ trợ!"
            }
            
    except Exception as e:
        return {
            "compatible": False,
            "message": f"Lỗi kiểm tra tương thích: {str(e)}"
        }


def get_copy_preview(test_file_path, doc_file_path):
    """
    Generate a preview of what will be copied
    
    Args:
        test_file_path (str): Path to mock documentation file  
        doc_file_path (str): Path to unit test file
        
    Returns:
        str: Preview text of the copy operation
    """
    try:
        test_name = os.path.basename(test_file_path)
        doc_name = os.path.basename(doc_file_path)
        
        # Try to get information about the source sheet
        preview_info = ""
        try:
            source_wb = load_workbook(test_file_path, data_only=True)
            sheet_name = "項目一覧"
            
            if sheet_name in source_wb.sheetnames:
                source_ws = source_wb[sheet_name]
                max_row = source_ws.max_row
                max_col = source_ws.max_column
                start_source_row = 5
                rows_to_copy = max_row - start_source_row + 1 if max_row >= start_source_row else 0
                preview_info = f"""
📊 Thông tin sheet nguồn:
• Sheet: {sheet_name}
• Tổng số dòng trong sheet: {max_row}
• Copy từ dòng: {start_source_row} đến {max_row}
• Số dòng sẽ copy: {rows_to_copy}
• Số cột: {max_col}
• Dữ liệu sẽ được paste từ dòng 6 trong file đích
                """
                source_wb.close()
            else:
                preview_info = f"\n⚠️ Không tìm thấy sheet '{sheet_name}' trong file mocks"
                
        except Exception as e:
            preview_info = f"\n⚠️ Không thể đọc thông tin sheet: {str(e)}"
        
        preview = f"""
📋 Thông tin sao chép dữ liệu:

📁 File mocks (nguồn): {test_name}
📄 File unit test (đích): {doc_name}

🔄 Các thao tác sẽ thực hiện:
• Đọc dữ liệu từ dòng 5 trở đi trong sheet "項目一覧" của file mocks
• Copy cả giá trị và formatting (borders, colors, fonts, merged cells)
• Paste vào sheet "項目一覧" của file unit test với đầy đủ style
• Vị trí paste: Bắt đầu từ dòng thứ 6
• Thêm outside border bao quanh vùng dữ liệu đã copy
• Copy toàn bộ dữ liệu từ sheet "data_1" và paste vào cột tiếp theo (dòng 5)
• Giữ nguyên cấu trúc merged cells (cells đã gộp)
• Tạo bảng với thin border bên dưới data_1 (từ dòng 9)
• Thêm thin border bên trong bảng để tạo lưới
• Xóa sheet "data_1" sau khi copy xong để dọn dẹp{preview_info}

⚡ Trạng thái: Sẵn sàng để thực hiện
        """
        
        return preview.strip()
        
    except Exception as e:
        return f"Lỗi tạo preview: {str(e)}" 
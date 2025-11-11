# Auto Review Tool

Auto Review Tool là một ứng dụng hỗ trợ kiểm tra, tạo mã nguồn và đánh giá chất lượng code Front-End (FE) và Back-End (BE) một cách hiệu quả, thông qua giao diện người dùng trực quan được xây dựng bằng Tkinter.

## Tính năng chính

- Tạo comment cho file source tự động (có hỗ trợ chọn ngày và tác giả)
- Sinh DTO từ file Excel
- Sinh Unit Test Template từ DTO
- Đếm số dòng code từ file Self-Check
- Tự động load danh sách file từ file self-check Excel
- Hỗ trợ Watchdog để reload app khi có thay đổi mã nguồn

---

## Cách cài đặt & chạy

### 1. Cài Python

Yêu cầu Python 3.8 trở lên  
Kiểm tra bằng:

```bash
python --version
```

### 2. (Tùy chọn) Tạo môi trường ảo

```bash
python -m venv venv
venv\Scripts\activate # Windows
# hoặc
source venv/bin/activate  # macOS/Linux
```

### 3. Cài các thư viện phụ thuộc

Nếu đã có `requirements.txt`:

```bash
pip install -r requirements.txt
```

Nếu chưa, bạn có thể tạo sau khi hoàn tất cài đặt bằng:

```bash
pip freeze > requirements.txt
```

### 4. Chạy ứng dụng

Chạy ứng dụng với hot reload

```bash
python autoReviewTool.py --watch
```

### 5. Command đóng gói ứng dụng

```bash
pyinstaller autoReviewTool.py --name NDSTools-v1.0.3 --onefile -w
```

# 🔧 Auto Review Tool

Auto Review Tool là một ứng dụng hỗ trợ kiểm tra, tạo mã nguồn và đánh giá chất lượng code Front-End (FE) và Back-End (BE) một cách hiệu quả, thông qua giao diện người dùng trực quan được xây dựng bằng Tkinter.

## ✨ Tính năng chính

- 🌐 Tạo comment cho file source tự động (có hỗ trợ chọn ngày và tác giả)
- 📄 Sinh DTO từ file Excel
- 🧪 Sinh Unit Test Template từ DTO
- 📊 Đếm số dòng code từ file Self-Check
- 📥 Tự động load danh sách file từ file self-check Excel
- 🔁 Hỗ trợ Watchdog để reload app khi có thay đổi mã nguồn

---

## 🚀 Cách cài đặt & chạy

### 1. Cài Python

Yêu cầu Python 3.8 trở lên  
Kiểm tra bằng:

```bash
python --version
```

python -m venv venv
venv\Scripts\activate # Windows

# hoặc

source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
pip freeze > requirements.txt
python autoReviewTool.py

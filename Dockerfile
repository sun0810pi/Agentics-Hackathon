FROM python:3.10-slim

WORKDIR /app

# Copy file requirements từ folder backend vào container
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code backend vào container
COPY backend ./backend
COPY frontend ./frontend

# Đặt thư mục làm việc là backend để Python tìm thấy module 'app'
WORKDIR /app/backend

# Chạy uvicorn trỏ vào app.main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Sử dụng một hình ảnh cơ sở Python
FROM python:3.7.9

# Đặt thư mục làm việc mặc định trong container
WORKDIR /app

# Sao chép tất cả các tệp yêu cầu (requirements.txt) vào thư mục /app
COPY requirements.txt .

# Cài đặt các gói phụ thuộc từ requirements.txt
RUN pip install -r requirements.txt

# Sao chép tất cả các tệp từ thư mục hiện tại vào thư mục /app trong container
COPY . .

# Chạy ứng dụng Flask khi container được khởi chạy
CMD ["python", "app.py"]

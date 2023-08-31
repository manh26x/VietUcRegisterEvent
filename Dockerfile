# Sử dụng một hình ảnh Python chứa Flask
FROM python:3.7.17-slim-bullseye

# Sao chép mã nguồn ứng dụng vào thư mục /app trong container
COPY . /app

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện Python cần thiết
RUN pip install -r requirements.txt

# Expose cổng 80 để sử dụng HTTP
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]

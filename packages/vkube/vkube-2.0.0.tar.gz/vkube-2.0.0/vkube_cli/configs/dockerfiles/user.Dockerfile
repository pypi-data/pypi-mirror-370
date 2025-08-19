FROM python:3.11-slim
WORKDIR /app
# 复制项目文件
COPY requirements.txt .
COPY app.py .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5009
CMD python3 /app/app.py

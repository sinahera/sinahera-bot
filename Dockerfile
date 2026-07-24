FROM python:3.11-slim

WORKDIR /app

# ابتدا setuptools را به‌روز می‌کنیم
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "robot.py"]

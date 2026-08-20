FROM python:3.10-slim

# pytgcalls এর জন্য প্রয়োজনীয় সব অডিও কম্পাইলার ও FFmpeg লাইব্রেরি
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip এবং wheel আপগ্রেড
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "bot.py"]

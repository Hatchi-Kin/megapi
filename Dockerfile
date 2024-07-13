FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libssl-dev \
    libffi-dev \
    ffmpeg \
    python3-dev \
    gcc \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /api

ADD . /api

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "app.py"]  
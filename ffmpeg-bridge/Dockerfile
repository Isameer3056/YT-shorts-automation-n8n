FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask
WORKDIR /app
COPY server.py /app/server.py
CMD ["python3", "server.py"]

FROM python:3.11-slim
RUN pip install --no-cache-dir wyoming flask
WORKDIR /app
COPY server.py /app/server.py
CMD ["python3", "server.py"]

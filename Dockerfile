FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY index.html .

EXPOSE 5005

CMD ["python", "./main.py"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Un solo worker: el registro de gestores de casos de uso vive en memoria.
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8020", "--workers", "1"]

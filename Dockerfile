FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# frontend-web must stay a sibling of backend/ — main.py resolves it via
# Path(__file__).parent.parent / "frontend-web" and mounts it at /static.
COPY backend/ backend/
COPY frontend-web/ frontend-web/

# .env is not baked in here (it holds real credentials) — pass it at
# `docker run` time with --env-file instead.

EXPOSE 8000
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

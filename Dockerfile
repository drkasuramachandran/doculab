FROM python:3.14-slim

# LibreOffice is needed for Word <-> PDF conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
      libreoffice-writer libreoffice-draw fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
RUN mkdir -p storage/uploads storage/outputs

ENV PORT=8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]

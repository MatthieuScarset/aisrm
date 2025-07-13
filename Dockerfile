FROM python:3.10-slim

# Install Python dependencies.
COPY requirements.txt .

RUN pip install -U pip \
    && pip install -r requirements.txt

# Copy backend application folder
COPY api api

# Copy frontend application folder
COPY app app

# Run backend application on default port
CMD ["sh", "-c", "uvicorn api.run:app --host 0.0.0.0 --port ${PORT}"]

FROM python:3.10-slim

# Build argument for environment
ARG ENV=dev

# Copy requirements files first
COPY requirements-*.txt ./

# Select the appropriate requirements file based on ENV
RUN cp requirements-${ENV}.txt requirements.txt

# Install Python dependencies and clean up in one layer
RUN pip install -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copy backend application folder
COPY api api

# Copy frontend application folder
COPY app app

# Run backend application on default port
CMD ["sh", "-c", "uvicorn api.run:app --host 0.0.0.0 --port ${PORT}"]

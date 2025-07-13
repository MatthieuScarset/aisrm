FROM python:3.10-slim

WORKDIR /app

COPY requirements-app.txt requirements.txt

RUN pip install -U pip \
    && pip install -r requirements.txt

COPY app/ ./app/

CMD ["streamlit", "run", "app/run.py"]

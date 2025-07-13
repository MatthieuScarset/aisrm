FROM python:3.10-slim-bookworm

COPY requirements.txt requirements.txt

RUN pip install -U pip cython wheel
RUN pip install -r requirements.txt

COPY api api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.run:app --host 0.0.0.0 --port ${PORT}"]

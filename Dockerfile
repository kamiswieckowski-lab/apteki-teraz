FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    DATA_DIR=/app/data \
    PORT=8000

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts ./scripts
COPY tests/fixtures ./tests/fixtures

RUN useradd --create-home app && mkdir -p /app/data && chown app /app/data
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/health')"

# Przy pierwszym starcie pobiera dane z dane.gov.pl, potem uruchamia serwer.
CMD ["sh", "-c", "python scripts/fetch_data.py --if-missing && uvicorn apteki.api:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]

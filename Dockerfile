FROM python:3.11-slim

WORKDIR /app

# Installer curl til healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Afhængigheder i eget lag så Docker kan cache dem
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiér kildekode
COPY . .

# Kør ikke som root
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health endpoint bruges af Docker og Azure til at tjekke om appen kører
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# gunicorn er mere stabil end Flask's dev-server i produktion
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--worker-tmp-dir", "/tmp", "app:app"]

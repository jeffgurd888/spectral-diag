FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY spectral_diag ./spectral_diag

RUN pip install --no-cache-dir .

ENV SPECTRAL_API_KEYS=""
EXPOSE 8000

# Run: docker run -p 8000:8000 -e SPECTRAL_API_KEYS="k1,k2" spectral-diag
CMD ["uvicorn", "spectral_diag.api:app", "--host", "0.0.0.0", "--port", "8000"]

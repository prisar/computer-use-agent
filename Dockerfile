FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt
RUN playwright install chromium --with-deps

COPY computer_use_agent ./computer_use_agent

EXPOSE 8000

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]

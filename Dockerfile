FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl netcat-traditional gcc \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

COPY . /app

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

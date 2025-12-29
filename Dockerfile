FROM python:3.12-slim

# Desativa o buffer do Python para logs em tempo real
ENV PYTHONUNBUFFERED=1

# Instala o uv
    #RUN pip install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copia os arquivos de dependências primeiro (melhor cache)
COPY pyproject.toml uv.lock ./

# Instala dependências
RUN uv sync --frozen --no-dev

# Copia o restante do código
COPY src ./src

CMD ["uv", "run", "python", "src/main.py"]

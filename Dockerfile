FROM python:3.12-slim

WORKDIR /app

# Instala o uv
RUN pip install uv

# Copia os arquivos de dependências primeiro (melhor cache)
COPY pyproject.toml uv.lock ./

# Instala dependências
RUN uv sync --frozen --no-dev

# Copia o restante do código
COPY src ./src

CMD ["uv", "run", "python", "src/main.py"]

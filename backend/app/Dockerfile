FROM python:3.11-slim-bullseye

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 先装依赖（用缓存）
COPY pyproject.toml uv.lock ./
RUN uv venv && uv sync --no-cache

# 再复制源码（关键！）
COPY . .

# 环境变量
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000
# Dockerfile 里
CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000", "--reload"]


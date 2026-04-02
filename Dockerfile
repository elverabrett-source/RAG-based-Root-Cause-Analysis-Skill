# 阶段 1: 环境构建
FROM python:3.10-slim as builder

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖（由于一些库需要编译，如果是轻量级安装建议预装）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 阶段 2: 生产运行环境
FROM python:3.10-slim

WORKDIR /app

# 从构建者阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p data/vector_db data/knowledge_base logs

# 开放 API 端口
EXPOSE 8000

# 启动 FastAPI 服务
# 建议通过环境变量注入 API KEY
CMD ["python", "scripts/server.py"]

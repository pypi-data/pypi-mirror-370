# 使用python:3-slim作为基础镜像进行多阶段构建

# 第一阶段：构建阶段
FROM python:3-slim AS builder

# 设置工作目录
WORKDIR /app

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖到一个独立目录，不依赖gcc编译
RUN pip install --no-cache-dir --user -r requirements.txt

# 第二阶段：运行时阶段
FROM python:3-slim

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的Python依赖
COPY --from=builder /root/.local /root/.local

# 确保Python依赖在PATH中
ENV PATH=/root/.local/bin:$PATH

# 复制项目源代码
COPY . .

# 设置环境变量
# 这些变量将在运行容器时被覆盖
ENV APP_ENV=production
ENV APP_DEBUG=false
ENV APP_HOST=0.0.0.0
ENV APP_PORT=10000
ENV GRPC_PORT=50051

# 暴露API和gRPC端口
EXPOSE $APP_PORT $GRPC_PORT

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# 定义启动命令，同时运行FastAPI和gRPC服务
CMD ["/bin/bash", "-c", "python -m src.main & python scripts/run_grpc_server.py"]

# {project_name} Makefile

# 项目信息
PROJECT_NAME={project_name}
VERSION={project_version}

# 虚拟环境配置
VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip

# 路径配置
SRC_DIR=src
TESTS_DIR=tests

# 构建目标
.PHONY: help venv install install-dev run test lint format clean docker-build docker-run

# 默认目标
help:
	@echo "可用命令："
	@echo "  make venv           - 创建虚拟环境"
	@echo "  make install        - 安装生产依赖"
	@echo "  make install-dev    - 安装开发依赖"
	@echo "  make run            - 运行应用程序"
	@echo "  make test           - 运行测试"
	@echo "  make lint           - 运行代码检查"
	@echo "  make format         - 格式化代码"
	@echo "  make clean          - 清理项目"
	@echo "  make docker-build   - 构建Docker镜像"
	@echo "  make docker-run     - 运行Docker容器"
	@echo "  make grpc-generate  - 生成gRPC代码"
	@echo "  make grpc-server    - 运行gRPC服务器"

# 创建虚拟环境
venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools

# 安装生产依赖
install:
	$(PIP) install -r requirements.txt

# 安装开发依赖
install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest flake8 black isort

# 运行应用程序
run:
	$(PYTHON) -m uvicorn $(SRC_DIR).main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	$(PYTHON) -m pytest $(TESTS_DIR) -v

# 运行代码检查
lint:
	$(PYTHON) -m flake8 $(SRC_DIR) $(TESTS_DIR)
	$(PYTHON) -m isort --check-only $(SRC_DIR) $(TESTS_DIR)
	$(PYTHON) -m black --check $(SRC_DIR) $(TESTS_DIR)

# 格式化代码
format:
	$(PYTHON) -m isort $(SRC_DIR) $(TESTS_DIR)
	$(PYTHON) -m black $(SRC_DIR) $(TESTS_DIR)

# 清理项目
clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/__pycache__
	rm -rf $(TESTS_DIR)/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf build dist $(PROJECT_NAME).egg-info

# 构建Docker镜像
docker-build:
	docker build -t $(PROJECT_NAME):$(VERSION) .

# 运行Docker容器
docker-run:
	docker run -p 8000:8000 --env-file .env $(PROJECT_NAME):$(VERSION)

# 生成gRPC代码
grpc-generate:
	$(PYTHON) scripts/generate_grpc_code.py

# 运行gRPC服务器
grpc-server:
	$(PYTHON) scripts/run_grpc_server.py
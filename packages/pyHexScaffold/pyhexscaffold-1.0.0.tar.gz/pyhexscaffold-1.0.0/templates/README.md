# {project_name}

版本: {project_version}

一个基于六边形架构的现代化Python应用程序，提供清晰的代码组织和良好的可测试性。

## 特性

- 🏗️ 基于六边形架构（端口和适配器模式）
- 🚀 使用FastAPI构建高性能API
- 💉 依赖注入（使用dependency-injector）
- 🔧 完整的环境变量配置系统
- 🐳 Docker容器化支持
- 🛠️ Makefile构建工具支持
- 🧪 完整的单元测试框架（pytest）
- 📚 详细的项目文档

## 快速开始

### 1. 克隆项目

```bash
# 克隆项目（示例）
git clone <repository-url>
cd {project_name}
```

### 2. 创建虚拟环境

```bash
make venv
```

### 3. 安装依赖

```bash
# 安装生产依赖
make install

# 或安装开发依赖（包含测试工具）
make install-dev
```

### 4. 配置环境变量

复制并编辑`.env`文件，根据您的环境进行配置。

### 5. 运行应用程序

```bash
make run
```

应用程序将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 查看。

## 项目结构

该项目采用六边形架构（端口和适配器模式）设计，清晰地分离了核心业务逻辑与外部依赖。

```
{project_name}/
├── src/
│   ├── adapters/       # 适配器层 - 与外部系统交互
│   │   ├── api/        # API接口适配器
│   │   ├── dtos/       # 数据传输对象
│   │   ├── events/     # 事件处理适配器
│   │   ├── grpc/       # gRPC适配器
│   │   └── repository/ # 数据存储适配器
│   ├── application/    # 应用层 - 协调领域对象和用例
│   ├── config/         # 配置模块
│   ├── domain/         # 领域层 - 核心业务逻辑和实体
│   ├── ports/          # 端口层 - 定义接口抽象
│   ├── proto/          # Protocol Buffers定义
│   ├── containers.py   # 依赖注入容器
│   ├── main.py         # 应用入口点
│   └── __init__.py
├── tests/              # 测试目录
│   ├── adapters/       # 适配器层测试
│   ├── application/    # 应用层测试
│   └── conftest.py     # 测试配置
├── scripts/            # 辅助脚本
├── docs/               # 项目文档
├── requirements.txt    # 项目依赖
├── Dockerfile          # Docker构建文件
├── Makefile            # 构建工具配置
├── .env                # 环境变量配置
├── .gitignore          # Git忽略文件
├── .dockerignore       # Docker忽略文件
└── README.md           # 项目说明文档
```

## 六边形架构概述

六边形架构（也称为端口和适配器模式）的核心思想是将应用程序的核心业务逻辑与外部系统解耦。

- **领域层**（Domain）：包含业务实体、值对象和领域服务，体现核心业务规则。
- **端口层**（Ports）：定义接口，描述核心领域需要与外部世界交互的方式。
- **应用层**（Application）：协调领域对象和端口，实现用例。
- **适配器层**（Adapters）：实现端口，将外部系统（如数据库、API客户端、UI等）连接到核心业务逻辑。

## 开发指南

### 运行测试

```bash
make test
```

### 代码检查

```bash
make lint
```

### 格式化代码

```bash
make format
```

### 构建Docker镜像

```bash
make docker-build
```

### 运行Docker容器

```bash
make docker-run
```

## 依赖注入

该项目使用`dependency-injector`库实现依赖注入，所有依赖项都在`src/containers.py`中定义。这种方式使代码更加模块化、可测试，并便于替换实现。

## 环境配置

所有环境配置都通过`.env`文件管理，并在`src/config/settings.py`中加载。这种方式使配置与代码分离，便于在不同环境中部署。

## 测试

测试使用`pytest`框架编写，位于`tests`目录下。测试按层组织，确保每个组件都能独立测试。

## Docker容器化

项目包含完整的Docker支持，可通过`make docker-build`和`make docker-run`命令快速构建和运行容器。

## 扩展指南

### 添加新的领域实体

1. 在`src/domain/entities.py`中定义实体类
2. 在`src/domain/events.py`中定义相关事件（如适用）

### 添加新的API端点

1. 在`src/adapters/api/router.py`中添加新的路由
2. 在`src/adapters/dtos/`中定义相关的数据传输对象

### 添加新的存储实现

1. 在`src/ports/repositories.py`中定义存储接口
2. 在`src/adapters/repository/`中实现该接口
3. 在`src/containers.py`中注册新的存储实现

## 文档

详细的项目文档可在`docs/hexagonal_architecture_scaffold.md`中找到，包含更多关于六边形架构的解释和项目的详细设计。

## 许可证

[MIT](LICENSE)
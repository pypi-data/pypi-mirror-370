# pyHexScaffold

[![PyPI version](https://badge.fury.io/py/pyHexScaffold.svg)](https://badge.fury.io/py/pyHexScaffold)

一个高效的六边形架构（端口和适配器模式）项目脚手架生成器，帮助你快速启动符合最佳实践的Python项目。

## 特性

- 🏗️ 生成符合六边形架构的项目结构
- 🚀 集成FastAPI框架支持
- 💉 内置依赖注入（使用dependency-injector）
- 🔧 完整的环境变量配置系统
- 🐳 Docker容器化支持
- 🛠️ Makefile构建工具支持
- 🧪 单元测试框架配置（pytest）
- 📚 详细的项目文档
- 🔧 gRPC支持

## 安装

使用pip安装pyHexScaffold：

```bash
pip install pyHexScaffold
```

或者从源码安装：

```bash
# 克隆项目
# git clone https://github.com/yourusername/pyHexScaffold.git
# cd pyHexScaffold

# 安装开发版本
pip install -e .
```

## 使用方法

安装完成后，可以通过命令行工具`pyhexscaffold`来生成新的项目：

```bash
# 基本用法
pyhexscaffold /path/to/project

# 自定义项目名称和版本
pyhexscaffold /path/to/project --name my_project --version 0.1.0

# 或者使用简写
pyhexscaffold /path/to/project -n my_project -v 0.1.0
```

### 命令行参数

- `project_path`: 项目路径（必需）
- `--name, -n`: 项目名称（默认：my_hexagonal_app）
- `--version, -v`: 项目版本（默认：1.0.0）

## 生成的项目结构

生成的项目采用六边形架构（端口和适配器模式）设计，清晰地分离了核心业务逻辑与外部依赖：

```
project_name/
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

六边形架构（也称为端口和适配器模式）的核心思想是将应用程序的核心业务逻辑与外部系统解耦：

- **领域层**（Domain）：包含业务实体、值对象和领域服务，体现核心业务规则。
- **端口层**（Ports）：定义接口，描述核心领域需要与外部世界交互的方式。
- **应用层**（Application）：协调领域对象和端口，实现用例。
- **适配器层**（Adapters）：实现端口，将外部系统（如数据库、API客户端、UI等）连接到核心业务逻辑。

## 开发指南

生成的项目包含详细的开发指南，您可以在生成的项目中的`docs/hexagonal_architecture_scaffold.md`文件中找到更多信息。

### 基本开发流程

1. 进入项目目录：`cd /path/to/project`
2. 创建虚拟环境：`make venv`
3. 激活虚拟环境：`source .venv/bin/activate`（Linux/Mac）或 `.venv\Scripts\activate`（Windows）
4. 安装依赖：`make install` 或 `make install-dev`（开发依赖）
5. 运行应用：`make run`
6. 运行测试：`make test`

## 示例

以下是一个基本的使用示例：

```python
# 生成一个名为 my_project 的新项目
pyhexscaffold ./my_project --name my_project

# 进入项目目录
cd my_project

# 创建虚拟环境
make venv

source .venv/bin/activate

# 安装依赖
make install-dev

# 运行应用
make run
```

应用程序将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 查看。

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎贡献代码！请先fork项目，然后提交pull request。

## 问题反馈

如有任何问题或建议，请在 [GitHub Issues](https://github.com/yourusername/pyHexScaffold/issues) 中提交。

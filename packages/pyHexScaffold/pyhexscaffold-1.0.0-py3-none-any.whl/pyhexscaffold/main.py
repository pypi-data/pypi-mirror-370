#!/usr/bin/env python3
"""六边形架构项目脚手架生成器

这个脚本可以生成一个符合六边形架构的Python项目脚手架，包含以下特性：
- FastAPI框架支持
- 依赖注入（使用dependency-injector）
- 环境变量配置（.env和config模块）
- Docker容器化支持
- Makefile构建工具支持
- 单元测试框架（pytest）
- 项目目录结构符合六边形架构规范
"""

import os
import sys
import argparse
import shutil
from datetime import datetime

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取包根目录
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
# 定义模板目录路径
TEMPLATES_DIR = os.path.join(PACKAGE_DIR, "templates")


def read_template_file(template_path):
    """从模板目录中读取模板文件内容"""
    full_path = os.path.join(TEMPLATES_DIR, template_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def create_directory_structure(project_path):
    """创建项目的目录结构"""
    # 定义项目目录结构
    directories = [
        f"{project_path}/src",
        f"{project_path}/src/adapters",
        f"{project_path}/src/adapters/api",
        f"{project_path}/src/adapters/dtos",
        f"{project_path}/src/adapters/events",
        f"{project_path}/src/adapters/grpc",
        f"{project_path}/src/adapters/repository",
        f"{project_path}/src/application",
        f"{project_path}/src/config",
        f"{project_path}/src/domain",
        f"{project_path}/src/ports",
        f"{project_path}/src/proto",
        f"{project_path}/tests",
        f"{project_path}/scripts",
        f"{project_path}/docs",
    ]

    # 创建目录
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print(f"已创建项目目录结构在 {project_path}")


def create_file(file_path, content):
    """创建文件并写入内容"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已创建文件: {file_path}")


def generate_basic_files(project_path, project_name, project_version):
    """生成项目的基础配置文件"""
    # 创建.gitignore文件
    gitignore_content = read_template_file(".gitignore")
    create_file(f"{project_path}/.gitignore", gitignore_content)

    # 创建.dockerignore文件
    dockerignore_content = read_template_file(".dockerignore")
    create_file(f"{project_path}/.dockerignore", dockerignore_content)

    # 创建.env文件
    env_content = read_template_file(".env")
    # 替换项目名称变量
    env_content = env_content.replace("{project_name}", project_name)
    create_file(f"{project_path}/.env", env_content)

    # 创建requirements.txt文件
    requirements_content = read_template_file("requirements.txt")
    create_file(f"{project_path}/requirements.txt", requirements_content)


def generate_dockerfile(project_path):
    """生成Dockerfile"""
    dockerfile_content = read_template_file("Dockerfile")
    create_file(f"{project_path}/Dockerfile", dockerfile_content)


def generate_makefile(project_path, project_name, project_version):
    """生成Makefile"""
    makefile_content = read_template_file("Makefile")
    # 替换项目名称和版本变量
    makefile_content = makefile_content.replace("{project_name}", project_name)
    makefile_content = makefile_content.replace("{project_version}", project_version)
    create_file(f"{project_path}/Makefile", makefile_content)


def generate_config_files(project_path):
    """生成配置相关文件"""
    # 创建src/config/__init__.py
    config_init_content = read_template_file("src/config/__init__.py")
    create_file(f"{project_path}/src/config/__init__.py", config_init_content)

    # 创建src/config/settings.py
    settings_content = read_template_file("src/config/settings.py")
    create_file(f"{project_path}/src/config/settings.py", settings_content)


def generate_domain_files(project_path):
    """生成领域层文件"""
    # 创建src/domain/__init__.py
    domain_init_content = read_template_file("src/domain/__init__.py")
    create_file(f"{project_path}/src/domain/__init__.py", domain_init_content)

    # 创建src/domain/entities.py
    entities_content = read_template_file("src/domain/entities.py")
    create_file(f"{project_path}/src/domain/entities.py", entities_content)

    # 创建src/domain/events.py
    events_content = read_template_file("src/domain/events.py")
    create_file(f"{project_path}/src/domain/events.py", events_content)


def generate_ports_files(project_path):
    """生成端口层文件"""
    # 创建src/ports/__init__.py
    ports_init_content = read_template_file("src/ports/__init__.py")
    create_file(f"{project_path}/src/ports/__init__.py", ports_init_content)

    # 创建src/ports/repositories.py
    repositories_content = read_template_file("src/ports/repositories.py")
    create_file(f"{project_path}/src/ports/repositories.py", repositories_content)

    # 创建src/ports/services.py
    services_content = read_template_file("src/ports/services.py")
    create_file(f"{project_path}/src/ports/services.py", services_content)


def generate_application_files(project_path):
    """生成应用层文件"""
    # 创建src/application/__init__.py
    application_init_content = read_template_file("src/application/__init__.py")
    create_file(f"{project_path}/src/application/__init__.py", application_init_content)

    # 创建src/application/services.py
    services_content = read_template_file("src/application/services.py")
    create_file(f"{project_path}/src/application/services.py", services_content)


def generate_adapters_files(project_path):
    """生成适配器层文件"""
    # 创建src/adapters/__init__.py
    adapters_init_content = read_template_file("src/adapters/__init__.py")
    create_file(f"{project_path}/src/adapters/__init__.py", adapters_init_content)

    # 创建src/adapters/api/__init__.py
    api_init_content = read_template_file("src/adapters/api/__init__.py")
    create_file(f"{project_path}/src/adapters/api/__init__.py", api_init_content)

    # 创建src/adapters/api/router.py
    router_content = read_template_file("src/adapters/api/router.py")
    create_file(f"{project_path}/src/adapters/api/router.py", router_content)

    # 创建src/adapters/dtos/__init__.py
    dtos_init_content = read_template_file("src/adapters/dtos/__init__.py")
    create_file(f"{project_path}/src/adapters/dtos/__init__.py", dtos_init_content)

    # 创建src/adapters/events/__init__.py
    events_init_content = read_template_file("src/adapters/events/__init__.py")
    create_file(f"{project_path}/src/adapters/events/__init__.py", events_init_content)

    # 创建src/adapters/repository/__init__.py
    repository_init_content = read_template_file("src/adapters/repository/__init__.py")
    create_file(
        f"{project_path}/src/adapters/repository/__init__.py", repository_init_content
    )


def generate_containers_file(project_path):
    """生成依赖注入容器文件"""
    # 创建src/containers.py
    containers_content = read_template_file("src/containers.py")
    create_file(f"{project_path}/src/containers.py", containers_content)


def generate_main_file(project_path):
    """生成主入口文件"""
    # 创建src/__init__.py
    src_init_content = read_template_file("src/__init__.py")
    create_file(f"{project_path}/src/__init__.py", src_init_content)

    # 创建src/main.py
    main_content = read_template_file("src/main.py")
    create_file(f"{project_path}/src/main.py", main_content)


def generate_test_files(project_path):
    """生成测试文件"""
    # 创建tests/__init__.py
    tests_init_content = read_template_file("tests/__init__.py")
    create_file(f"{project_path}/tests/__init__.py", tests_init_content)

    # 创建tests/conftest.py
    conftest_content = read_template_file("tests/conftest.py")
    create_file(f"{project_path}/tests/conftest.py", conftest_content)


def generate_script_files(project_path):
    """生成脚本文件"""
    # 创建scripts/generate_grpc_code.py
    generate_grpc_code_content = read_template_file("scripts/generate_grpc_code.py")
    create_file(
        f"{project_path}/scripts/generate_grpc_code.py", generate_grpc_code_content
    )

    # 设置脚本可执行权限
    os.chmod(f"{project_path}/scripts/generate_grpc_code.py", 0o755)


def generate_proto_file(project_path):
    """生成示例proto文件"""
    # 创建src/proto/service.proto
    proto_content = read_template_file("src/proto/service.proto")
    create_file(f"{project_path}/src/proto/service.proto", proto_content)


def generate_docs_file(project_path):
    """生成文档文件"""
    # 创建docs/hexagonal_architecture_scaffold.md
    # docs_content = read_template_file("docs/hexagonal_architecture_scaffold.md")
    # create_file(f"{project_path}/docs/hexagonal_architecture_scaffold.md", docs_content)
    pass


def generate_readme_file(project_path, project_name, project_version):
    """生成README文件"""
    # 创建README.md
    # 由于在提取模板时未找到readme_content，这里我们手动创建一个基本的README
    readme_content = f"""# {project_name}

> 六边形架构示例项目

## 项目介绍

这是一个基于六边形架构（端口和适配器架构）的Python项目脚手架，集成了FastAPI、依赖注入、Docker等现代Python开发技术。

## 特性

- ✨ **六边形架构设计**：清晰的分层结构，核心业务逻辑与外部系统解耦
- 🚀 **FastAPI框架**：高性能的API框架，自动生成交互式文档
- 💉 **依赖注入**：使用dependency-injector实现依赖注入
- 🐳 **Docker支持**：多阶段构建，优化镜像大小
- 🧪 **单元测试**：集成pytest测试框架
- 🛠 **Makefile工具链**：简化开发和部署流程
- 🔧 **环境配置**：使用.env和pydantic-settings管理配置

## 快速开始

### 前提条件

- Python 3.8+ 
- Docker (可选)
- Git

### 安装依赖

```bash
# 创建虚拟环境
make venv

# 激活虚拟环境
source .venv/bin/activate

# 或直接安装依赖
make install
```

### 运行开发服务器

```bash
make run
```

这将启动带有热重载功能的FastAPI开发服务器，访问 http://localhost:10000/docs 查看API文档。

### 运行测试

```bash
make test
```

### 构建Docker镜像

```bash
make build
```

### 运行Docker容器

```bash
make docker-run
```

## 项目结构

请参考 docs/hexagonal_architecture_scaffold.md 了解详细的项目结构和架构说明。
"""
    create_file(f"{project_path}/README.md", readme_content)


def generate_project(project_path, project_name, project_version):
    """生成完整的项目脚手架"""
    # 创建目录结构
    create_directory_structure(project_path)

    # 生成基础配置文件
    generate_basic_files(project_path, project_name, project_version)

    # 生成Dockerfile
    generate_dockerfile(project_path)

    # 生成Makefile
    generate_makefile(project_path, project_name, project_version)

    # 生成配置文件
    generate_config_files(project_path)

    # 生成领域层文件
    generate_domain_files(project_path)

    # 生成端口层文件
    generate_ports_files(project_path)

    # 生成应用层文件
    generate_application_files(project_path)

    # 生成适配器层文件
    generate_adapters_files(project_path)

    # 生成依赖注入容器文件
    generate_containers_file(project_path)

    # 生成主入口文件
    generate_main_file(project_path)

    # 生成测试文件
    generate_test_files(project_path)

    # 生成脚本文件
    generate_script_files(project_path)

    # 生成proto文件
    generate_proto_file(project_path)

    # 生成文档文件
    generate_docs_file(project_path)

    # 生成README文件
    generate_readme_file(project_path, project_name, project_version)


def main():
    """主函数，解析命令行参数并生成项目"""
    parser = argparse.ArgumentParser(description="生成六边形架构项目脚手架")
    parser.add_argument("project_path", help="项目路径")
    parser.add_argument("--name", "-n", default="my_hexagonal_app", help="项目名称")
    parser.add_argument("--version", "-v", default="1.0.0", help="项目版本")

    args = parser.parse_args()

    # 确保项目路径存在
    project_path = os.path.abspath(args.project_path)

    # 如果项目路径已存在，则询问是否覆盖
    if os.path.exists(project_path):
        response = input(f"项目路径 '{project_path}' 已存在，是否覆盖？(y/n): ")
        if response.lower() != "y":
            print("取消生成项目")
            return
        # 清空目录
        shutil.rmtree(project_path)

    # 生成项目
    generate_project(project_path, args.name, args.version)

    print(f"项目 '{args.name}' 已成功生成在 '{project_path}'")
    print("\n接下来可以执行以下命令开始开发:")
    print(f"cd {project_path}")
    print("make venv")
    print("source .venv/bin/activate")
    print("make run")


if __name__ == "__main__":
    main()

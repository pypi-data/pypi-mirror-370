#!/usr/bin/env python
import os
import sys
from grpc_tools import protoc


def generate_grpc_code():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 项目根目录
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    # proto文件目录
    proto_dir = os.path.join(project_root, "src", "proto")
    # 生成的代码存放目录
    output_dir = os.path.join(project_root, "src", "adapters", "grpc")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有proto文件
    proto_files = []
    for file in os.listdir(proto_dir):
        if file.endswith(".proto"):
            proto_files.append(os.path.join(proto_dir, file))

    if not proto_files:
        print("No proto files found in {}".format(proto_dir))
        sys.exit(1)

    # 生成gRPC代码
    for proto_file in proto_files:
        print(f"Generating code for {proto_file}...")

        # 设置protoc参数
        args = [
            "grpc_tools.protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            proto_file,
        ]

        # 执行protoc命令
        if protoc.main(args) != 0:
            print(f"Error generating code for {proto_file}")
            sys.exit(1)

    print("All gRPC code generated successfully!")


if __name__ == "__main__":
    generate_grpc_code()

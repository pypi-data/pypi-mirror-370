"""pyHexScaffold - 六边形架构项目脚手架生成器

这个包提供了一个命令行工具，可以快速生成符合六边形架构的Python项目脚手架。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "六边形架构项目脚手架生成器"

from .main import generate_project, main

__all__ = [
    "generate_project",
    "main",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]
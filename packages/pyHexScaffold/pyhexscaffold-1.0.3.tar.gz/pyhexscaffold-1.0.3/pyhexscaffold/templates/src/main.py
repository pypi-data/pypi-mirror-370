"""数据服务主入口

FastAPI应用程序的主入口文件，配置应用程序、依赖注入和路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import config
from src.containers import Container


# 创建依赖注入容器实例
container = Container()


# 创建FastAPI应用程序实例
app = FastAPI(
    title=config.APP_NAME,
    debug=config.APP_DEBUG,
    description="",
    version=config.APP_VERSION,
    # 配置OpenAPI文档路径
    openapi_url="/openapi.json",
    # 配置Swagger UI文档路径
    docs_url="/docs",
    # 配置ReDoc文档路径
    redoc_url="/redoc",
)

# 配置CORS
origins = config.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health", tags=["health"])
def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "app_name": config.APP_NAME,
        "environment": config.APP_ENV,
        "version": config.APP_VERSION,
    }


# 开发环境运行应用程序的代码
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.APP_DEBUG,
    )

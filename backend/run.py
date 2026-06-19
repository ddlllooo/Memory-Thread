"""启动脚本"""
import os
import uvicorn

if __name__ == "__main__":
    # 生产环境禁用 reload
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=not is_production,
        workers=1 if is_production else None,
    )

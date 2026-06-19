import logging
import warnings
from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)

DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "mysql+pymysql://root:password@localhost:3306/memory_thread"

    # JWT 配置
    secret_key: str = DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 管理员账号配置
    admin_username: str = "admin"
    admin_password: str = "admin123"
    admin_email: str = "admin@example.com"

    # 文件上传配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # CORS 配置
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    settings = Settings()
    if settings.secret_key == DEFAULT_SECRET_KEY:
        warnings.warn(
            "SECRET_KEY 使用了默认值，请在 .env 中设置一个安全的密钥！",
            stacklevel=2,
        )
        logger.warning("SECRET_KEY 使用了默认值，这在生产环境中不安全！")
    if settings.admin_password == "admin123":
        warnings.warn(
            "ADMIN_PASSWORD 使用了默认值，请在 .env 中设置一个安全的密码！",
            stacklevel=2,
        )
        logger.warning("ADMIN_PASSWORD 使用了默认值，这在生产环境中不安全！")
    return settings

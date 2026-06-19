"""数据库初始化脚本"""

from sqlalchemy import text
from app.config import get_settings
from app.models.database import engine, Base, SessionLocal, User
from app.services.auth import get_password_hash

settings = get_settings()


def init_database():
    """初始化数据库（重建所有表）"""
    print("正在删除旧表...")
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.execute(text("DROP TABLE IF EXISTS images"))
        conn.execute(text("DROP TABLE IF EXISTS posts"))
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    print("旧表已删除")

    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    # 创建管理员账户（从 .env 配置读取）
    db = SessionLocal()
    try:
        print("正在创建管理员账户...")
        admin = User(
            username=settings.admin_username,
            email=settings.admin_email,
            hashed_password=get_password_hash(settings.admin_password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print("管理员账户创建完成")
        print(f"用户名: {settings.admin_username}")
        print("密码: 已从 .env 文件读取")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

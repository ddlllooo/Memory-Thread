"""数据库初始化脚本"""

from app.config import get_settings
from app.models.database import engine, Base, SessionLocal, User
from app.services.auth import get_password_hash

settings = get_settings()


def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    # 创建默认管理员账户
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("正在创建默认管理员账户...")
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("默认管理员账户创建完成")
            print("用户名: admin")
            print("密码: admin123")
        else:
            print("管理员账户已存在")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

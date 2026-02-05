"""
数据库连接管理
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from loguru import logger

from app.utils.config import settings

# 确保数据目录存在
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite特有配置
    echo=settings.debug  # 调试模式打印SQL
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()


def get_db() -> Session:
    """
    数据库会话依赖注入
    使用方式：
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表
    """
    from app.models import orm  # 导入ORM模型

    logger.info("🔧 初始化数据库...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库初始化完成")


def ensure_schema():
    """
    轻量级迁移：补齐缺失字段
    """
    try:
        with engine.begin() as conn:
            # books.parse_stats
            result = conn.execute(text("PRAGMA table_info(books)"))
            columns = {row[1] for row in result.fetchall()}
            if "parse_stats" not in columns:
                logger.info("🔧 发现缺失列 books.parse_stats，执行迁移...")
                conn.execute(text("ALTER TABLE books ADD COLUMN parse_stats JSON"))
                logger.info("✅ 已补齐 books.parse_stats")

            # author_personas.version
            result = conn.execute(text("PRAGMA table_info(author_personas)"))
            columns = {row[1] for row in result.fetchall()}
            if "version" not in columns:
                logger.info("🔧 发现缺失列 author_personas.version，执行迁移...")
                conn.execute(text("ALTER TABLE author_personas ADD COLUMN version VARCHAR"))
                logger.info("✅ 已补齐 author_personas.version")
            if "evidence_links" not in columns:
                logger.info("🔧 发现缺失列 author_personas.evidence_links，执行迁移...")
                conn.execute(text("ALTER TABLE author_personas ADD COLUMN evidence_links JSON"))
                logger.info("✅ 已补齐 author_personas.evidence_links")
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")


def drop_db():
    """
    删除所有表（谨慎使用！）
    """
    from app.models import orm  # 导入ORM模型

    logger.warning("⚠️  删除所有数据库表...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("🗑️  所有表已删除")


if __name__ == "__main__":
    # 测试数据库连接
    init_db()
    logger.info("✅ 数据库连接测试成功")

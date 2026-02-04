"""
配置管理模块
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # OpenAI API配置
    openai_api_key: str = "sk-test-key"  # 开发模式默认值，生产环境需在.env中配置真实密钥
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7

    # 项目配置
    project_name: str = "AI著作跨时空对话播客"
    project_version: str = "1.0.0"
    debug: bool = True

    # 文件路径
    books_dir: Path = Path("./data/books")
    output_dir: Path = Path("./data/output")
    prompts_dir: Path = Path("./data/prompts")
    logs_dir: Path = Path("./logs")

    # 数据库配置
    database_url: str = "sqlite:///./data/dialogue_podcast.db"

    # 内容生成配置
    episodes_per_book: int = 10
    min_episode_duration: int = 25
    max_episode_duration: int = 35

    # 热点匹配配置
    hot_topic_update_interval: int = 24
    hot_topic_relevance_threshold: float = 0.8

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()

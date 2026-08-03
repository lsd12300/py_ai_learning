# -*- coding: utf-8 -*-
# 配置类

import os
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict



# --------- 各模块配置类 ---------
class MemoryConfig(BaseModel):
    """记忆系统配置"""
    storage_dir: str = Field("", description="记忆文件目录")
    mode: str = Field("", description="记忆存储格式" )
    max_items: int = Field(100, description="最大记忆条数")

class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field("INFO", description="日志级别")
    format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式")



# --------- 总配置类 ---------
class Settings(BaseSettings):
    """总配置类"""

    # LLM
    api_key: str = Field("", description="API密钥")
    base_url: str = Field("", description="API基础URL")
    model_name: str = Field("", description="模型名称")

    timestamp_format: str = "%Y-%m-%d %H:%M:%S"  # 时间戳格式


    # 各模块配置（嵌套定义）
    memory: MemoryConfig = MemoryConfig()
    # logging: LoggingConfig


    # Pydantic Settings的模型配置
    model_config = SettingsConfigDict(
        env_file=os.path.join(str(Path(__file__).parent.parent), ".env"),  # 显式指定环境变量文件路径，确保在不同目录下也能正常工作
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # 嵌套环境变量分隔符 MEMOTY__**
        extra="ignore",         # 未定义环境变量处理方式： allow, ignore, forbid
        case_sensitive=False,   # 大小写敏感
        # env_prefix="APP_",    # 环境变量前缀 API_KEY -> APP_API_KEY
    )


def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()

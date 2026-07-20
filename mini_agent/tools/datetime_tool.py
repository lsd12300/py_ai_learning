# -*- coding: utf-8 -*-
# 日期时间工具

from datetime import datetime
import pytz


def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间, 默认北京时间"""
    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        # 未知时区, 使用默认时区
        timezone = "Asia/Shanghai"
        tz = pytz.timezone(timezone)

    now = datetime.now(tz)
    return now.strftime(f"%Y年%m月%d日 %H:%M:%S ({timezone})")


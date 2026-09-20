import os
import sys

from loguru import logger

LOG_DIR = "/var/log/order"

# 先移除默认的 stderr handler，避免重复输出
logger.remove()

# 控制台（始终启用）
logger.add(sys.stderr, level="DEBUG")

# 文件写入
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.add(
        os.path.join(LOG_DIR, "app.log"),
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留 30 天
        encoding="utf-8",
        level="INFO",
    )
except (PermissionError, OSError) as e:
    logger.warning("无法写入日志文件 ({})，仅输出到控制台", e)

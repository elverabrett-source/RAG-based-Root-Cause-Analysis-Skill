import sys
from loguru import logger
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置 Loguru 日志输出
# 1. 输出到控制台（带颜色）
# 2. 输出到文件（按大小轮转，保留 7 天）
config = {
    "handlers": [
        {
            "sink": sys.stdout, 
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "colorize": True
        },
        {
            "sink": LOG_DIR / "rca_service.log", 
            "serialize": True, # 输出 JSON 格式，方便 ELK 采集
            "rotation": "50 MB",
            "retention": "7 days",
            "compression": "zip"
        }
    ]
}

def setup_logging():
    logger.configure(**config)
    logger.info("[✓] 企业级结构化日志系统初始化完成。")

if __name__ == "__main__":
    setup_logging()
    logger.info("测试日志信息")
    logger.error("测试错误信息")

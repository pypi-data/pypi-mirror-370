import sys
from pathlib import Path

DEFAULT_LOG_PATH = Path("~/com-tools/logs/").expanduser().resolve()
DEFAULT_LOG_PATH.mkdir(parents=True, exist_ok=True)

from loguru import logger
# Adding custom level
logger.level("FATAL", no=60, color="<red>", icon="⛔⛔⛔")
logger.remove(0)
logger.add(sys.stderr, format="{time} | {level} | {level.icon} {message}")
logger.add(f"{DEFAULT_LOG_PATH}/com_tools.log", format="{time} | {level} | {level.icon} {message} ({extra})", level="DEBUG")
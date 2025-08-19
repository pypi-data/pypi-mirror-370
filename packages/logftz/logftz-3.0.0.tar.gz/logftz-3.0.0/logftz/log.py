from loguru import logger
from datetime import datetime
import pytz
import os, sys


class LoggerConfig:
    def __init__(self, timezone='Asia/Shanghai'):
        self.timezone = pytz.timezone(timezone)
        self._setup_logger()
    
    def format_time(self, record):
        local_time = record["time"].astimezone(self.timezone)
        record["time"] = local_time
        return True
    
    def _setup_logger(self):
        logger.remove()
        fmt = '{time:MM-DD HH:mm:ss}|{level}|{message}'
        cur_date = datetime.now(tz=self.timezone).strftime('%Y-%m-%d')
        os.makedirs('logs', exist_ok=True)
        logger.add(f'logs/{cur_date}.log',
                  level='INFO',
                  format=fmt,
                  filter=self.format_time,
                  rotation="1 day",
                  retention=3)
        logger.add(sys.stdout,
                  level='INFO',
                  format=fmt,
                  filter=self.format_time)
    
    def set_timezone(self, timezone):
        self.timezone = pytz.timezone(timezone)
        self._setup_logger()


_default_config = LoggerConfig()
logger_instance = logger
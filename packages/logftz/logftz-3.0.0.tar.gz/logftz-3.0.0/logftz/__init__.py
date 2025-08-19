from .log import logger_instance as logger, LoggerConfig, _default_config

__version__ = "1.0.0"
__all__ = ["logger", "LoggerConfig", "set_timezone"]


def set_timezone(timezone):
    """Set the timezone for logging.
    
    Args:
        timezone (str): Timezone string (e.g., 'Asia/Shanghai', 'UTC', 'America/New_York')
    """
    _default_config.set_timezone(timezone)
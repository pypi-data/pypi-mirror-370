"""
Convenience log functions and global logger instance for LogicPwn.
"""
from typing import Any, Dict, Optional
from .logger import LogicPwnLogger

logger = LogicPwnLogger()

def log_request(method: str, url: str, headers: Optional[Dict] = None,
                params: Optional[Dict] = None, body: Optional[Any] = None,
                timeout: Optional[int] = None):
    logger.log_request(method, url, headers, params, body, timeout)

def log_response(status_code: int, headers: Optional[Dict] = None,
                 body: Optional[Any] = None, response_time: Optional[float] = None):
    logger.log_response(status_code, headers, body, response_time)

def log_error(error: Exception, context: Optional[Dict] = None):
    logger.log_error(error, context)

def log_info(message: str, data: Optional[Dict] = None):
    logger.log_info(message, data)

def log_debug(message: str, data: Optional[Dict] = None):
    logger.log_debug(message, data)

def log_warning(message: str, data: Optional[Dict] = None):
    logger.log_warning(message, data) 
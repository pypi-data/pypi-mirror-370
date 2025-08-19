# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:59
# @Description:


"""
Logging configuration for PyGard client.
"""

import logging
import sys
from typing import Optional
import structlog


def setup_logger(
        level: str = "INFO",
        format_type: str = "json",
        log_file: Optional[str] = None
) -> structlog.stdlib.BoundLogger:
    """
    Setup structured logging for PyGard client.
    
    Args:
        level: Logging level
        format_type: Log format type (json or text)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if not log_file else open(log_file, "w"),
        level=getattr(logging, level.upper())
    )

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str = "pygard") -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return structlog.get_logger(name)

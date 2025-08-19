from abc import ABC
from logging import WARNING
from typing import Any, Dict, Optional

from galileo_core.helpers.logger import logger


class BaseGalileoException(Exception, ABC):
    """Base exception for all exceptions in galileo."""

    LOG_LEVEL: int = WARNING

    def __init__(self, message: str, logging_extra: Optional[Dict[str, Any]] = None) -> None:
        logger.log(self.LOG_LEVEL, message, extra=logging_extra)
        self.message: str = message
        super().__init__(self.message)

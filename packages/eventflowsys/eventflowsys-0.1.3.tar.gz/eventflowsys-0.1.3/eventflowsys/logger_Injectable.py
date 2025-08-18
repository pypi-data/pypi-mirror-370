from abc import ABC, abstractmethod
from loguru import logger as loguru_logger


__all__ = ["LoggerInjectable", "loguru_logger"]

class LoggerInjectable(ABC):
    """
    Abstract base class for logger injection.

    Provides a logger instance to subclasses, following the Dependency Inversion Principle.
    """

    def __init__(self, logger=None, log_path=None):
        """
        Initialize the logger, using dependency injection if provided.

        Args:
            logger: Optional custom logger instance.
            log_path: Optional log file path for the logger.
        """
        self.logger = logger or self._create_logger(log_path=log_path)

    @classmethod
    def _create_logger(cls, log_path=None):
        """
        Create and configure a logger instance for the subclass.

        Args:
            log_path: Optional log file path for the logger.

        Returns:
            loguru_logger: Configured logger instance.
        """
        logger = loguru_logger.bind(classname=cls.__name__)
        path = log_path if log_path is not None else f"logs/{cls.__name__}.log"
        logger.add(
            path,
            rotation="1 day",
            retention="7 days",
            level="INFO",
            filter=lambda record: record["extra"].get("classname") == cls.__name__
        )
        logger.info(f"{cls.__name__} logger initialized.")
        return logger

    @abstractmethod
    def perform_action(self):
        """
        Abstract method to be implemented by subclasses, using the injected logger.
        """
        pass



def __init__():
    """
    LoggerInjectable module initializer.
    """
    pass
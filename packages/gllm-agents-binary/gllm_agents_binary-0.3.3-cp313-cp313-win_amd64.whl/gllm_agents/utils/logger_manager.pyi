import logging
from _typeshed import Incomplete

BOSA_CORE_AVAILABLE: bool
DEFAULT_LOG_FORMAT: Incomplete
DEFAULT_DATE_FORMAT: str
LOG_COLORS: Incomplete

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors based on log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message with color codes.
        """

class LoggerManager:
    '''A singleton class to manage logging configuration.

    This class ensures that the root logger is initialized only once and is used across the application.

    Example to get and use the logger:
    ```python
    manager = LoggerManager()

    logger = manager.get_logger()

    logger.info("This is an info message")
    ```

    Example to set logging configuration:
    ```python
    manager = LoggerManager()

    manager.set_level(logging.DEBUG)
    manager.set_log_format(custom_log_format)
    manager.set_date_format(custom_date_format)
    ```

    Example to add a custom handler:
    ```python
    manager = LoggerManager()

    handler = logging.FileHandler("app.log")
    manager.add_handler(handler)
    ```

    Output format example:
    ```python
    [16/04/2025 15:08:18.323 GDPLabsGenAILogger INFO] Loading prompt_builder catalog for chatbot `general-purpose`
    ```
    '''
    def __new__(cls):
        """Initialize the singleton instance."""
    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance.

        This method returns a logger instance that is a child of the root logger. If name is not provided,
        the root logger will be returned instead.

        Args:
            name (str | None, optional): The name of the child logger.
                If None, the root logger will be returned. Defaults to None.

        Returns:
            logging.Logger: Configured logger instance.
        """
    def set_level(self, level: int) -> None:
        """Set logging level for all loggers in the hierarchy.

        Args:
            level (int): The logging level to set (e.g., logging.INFO, logging.DEBUG).
        """
    def set_log_format(self, log_format: str) -> None:
        """Set logging format for all loggers in the hierarchy.

        Args:
            log_format (str): The log format to set.
        """
    def set_date_format(self, date_format: str) -> None:
        """Set date format for all loggers in the hierarchy.

        Args:
            date_format (str): The date format to set.
        """
    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom handler to the root logger.

        Args:
            handler (logging.Handler): The handler to add to the root logger.
        """

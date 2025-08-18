from eventflowsys import LoggerInjectable
import pytest 

class DataProcessor(LoggerInjectable):
    """
    Example subclass that processes data and logs the action.
    """
    def perform_action(self):
        self.logger.info("Processing data in DataProcessor.")

class NotificationSender(LoggerInjectable):
    """
    Example subclass that sends notifications and logs the action.
    """
    def perform_action(self):
        self.logger.info("Sending notification in NotificationSender.")

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    def bind(self, **kwargs):
        return self
    def add(self, *args, **kwargs):
        pass

def test_data_processor_logs():
    logger = DummyLogger()
    processor = DataProcessor(logger=logger)
    processor.perform_action()
    assert "Processing data in DataProcessor." in logger.messages

def test_notification_sender_logs():
    logger = DummyLogger()
    sender = NotificationSender(logger=logger)
    sender.perform_action()
    assert "Sending notification in NotificationSender." in logger.messages

def test_data_processor_logs_with_loguru(caplog):
    from loguru import logger as loguru_logger
    import sys
    messages = []
    def sink(msg):
        messages.append(msg)
    loguru_logger.remove()
    loguru_logger.add(sink, format="{message}")
    processor = DataProcessor(logger=loguru_logger)
    processor.perform_action()
    assert any("Processing data in DataProcessor." in m for m in messages)

def test_data_processor_default_logger(tmp_path):
    import os
    # Ensure .pytest_cache/logs directory exists
    cache_logs_dir = os.path.join(os.getcwd(), ".pytest_cache", "logs")
    os.makedirs(cache_logs_dir, exist_ok=True)
    # Patch loguru to write logs to .pytest_cache/logs
    from loguru import logger as loguru_logger
    loguru_logger.remove()
    log_path = os.path.join(cache_logs_dir, "DataProcessor.log")
    loguru_logger.add(log_path, rotation="1 day", retention="7 days", level="INFO")
    processor = DataProcessor(log_path=log_path)
    processor.perform_action()
    assert os.path.exists(log_path)
    with open(log_path, "r") as f:
        contents = f.read()
    assert "Processing data in DataProcessor." in contents


import pytest
from loguru import logger

from wujing.utils.logger import configure_logger


@pytest.mark.skip()
def test_configure_logger_stdout():
    configure_logger(sink="stdout")
    logger.info("Test message to stdout")


@pytest.mark.skip()
def test_configure_logger_file(tmp_path):
    log_file = tmp_path / "test.log"
    print(f"{log_file=}")
    configure_logger(log_file_name=str(log_file), sink="file")
    logger.info("Test message to file")
    logger.stop()


def test_configure_stdout_and_file(tmp_path):
    log_file = tmp_path / "test.log"
    print(f"{log_file=}")
    configure_logger(log_file_name=str(log_file), sink=["stdout", "file"])
    logger.info("Test message to both stdout and file")
    logger.stop()

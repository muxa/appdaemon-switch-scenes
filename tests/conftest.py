import logging.config


def pytest_configure(config):
    logging.config.fileConfig("logging_config_test.ini")

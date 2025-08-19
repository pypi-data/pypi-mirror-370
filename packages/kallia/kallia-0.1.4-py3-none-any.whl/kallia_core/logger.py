import sys
import logging


class Logger:
    @staticmethod
    def config(logger: logging.Logger) -> None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

from logging import Formatter, StreamHandler, getLogger

AMPLIFY_BBOPT_LOGGER_NAME = "amplify_bbopt"  # The name used for the Amplify black-box optimization logger.

AMPLIFY_BBOPT_LOG_FORMATTER = Formatter(
    f"[%(asctime)s] [{AMPLIFY_BBOPT_LOGGER_NAME}] [%(levelname).4s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)  # Logging formatter for Amplify BBOpt.


def set_amplify_bbopt_logger() -> None:
    """Set up the logger for the Amplify BBOpt module."""
    logger = getLogger(AMPLIFY_BBOPT_LOGGER_NAME)
    logger.propagate = False
    logger.setLevel("INFO")
    # set handler
    handler = StreamHandler()
    handler.setFormatter(AMPLIFY_BBOPT_LOG_FORMATTER)
    logger.handlers = [handler]


set_amplify_bbopt_logger()

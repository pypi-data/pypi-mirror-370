import logging
import os
import traceback



class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass


def setup_logging() -> None:
    env_log_level = os.getenv("LOG_LEVEL", "INFO")
    env_log_file = os.getenv("LOG_FILE", "log/xga.log")
    log_level = getattr(logging, env_log_level.upper(), logging.INFO)

    log_dir = os.path.dirname(env_log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    else:
        os.remove(env_log_file)

    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    import colorlog

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }

    console_formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(white)s%(message)s',
        log_colors=log_colors,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s -%(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(env_log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)

    logging.info(f"Logger is initialized, log_level={env_log_level}, log_file={env_log_file}")


def handle_error(e: Exception) -> None:
    logging.error("An error occurred: %s", str(e))
    logging.error("Traceback details:\n%s", traceback.format_exc())
    raise (e) from e

def setup_xga_env() -> None:
    from dotenv import load_dotenv
    load_dotenv()
    setup_logging()


if __name__ == "__main__":
    try:
        setup_xga_env()
    except Exception as e:
        handle_error(e)
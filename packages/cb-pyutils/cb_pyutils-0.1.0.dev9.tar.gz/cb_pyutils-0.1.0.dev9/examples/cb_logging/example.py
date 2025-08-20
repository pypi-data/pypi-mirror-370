
from cb_logging import CBLogger


def main_stdout():
    """Main function for logging to stdout."""
    log = CBLogger()

    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message.")


def main_stdout_file():
    """Main function for logging to stout and a file."""

    log = CBLogger(do_file_logging=True,
                   log_file_name='example.log')

    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message.")


if __name__ == "__main__":
    main_stdout()

    main_stdout_file()

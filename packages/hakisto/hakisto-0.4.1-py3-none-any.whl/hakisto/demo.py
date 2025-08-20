from hakisto import logger


def color():

    logger.trace("Trace")
    logger.debug("Debug")
    logger.verbose("Verbose")
    logger.info("Info")
    logger.success("Success")
    logger.warning("Warning")
    logger.error("Error")


def critical():
    s = "Hakisto"
    msg = f"Colors with {s} is easy!"  # noqa: F841
    logger.critical("A critical issue!")


def traceback():
    s = "Hakisto"
    msg = f"Colors with {s} is easy!"  # noqa: F841
    b = s[10]  # noqa: F841


if __name__ == "__main__":
    color()
    critical()
    traceback()

import logging
botocross_log = logging.getLogger('botocross')

def configure_logging(logger, level):
    logger.setLevel(getattr(logging, level.upper()))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger.getEffectiveLevel())
    logger.addHandler(console_handler)

class ExitCodes:
    (OK, FAIL) = range(0, 2)

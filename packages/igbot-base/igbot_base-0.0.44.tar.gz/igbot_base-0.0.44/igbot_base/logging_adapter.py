import logging

try:
    import structlog

    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False


def get_logger(name: str):
    if USE_STRUCTLOG:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)

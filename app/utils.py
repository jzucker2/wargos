import logging


def set_up_logging(level=logging.DEBUG):
    format = "[%(levelname)s] %(asctime)s %(message)s"
    logging.basicConfig(format=format, level=level)


# pass in __name__
def get_logger(name):
    try:
        from flask import current_app as app
    except ImportError:
        print('import error, using a system logger')
        return logging.getLogger(name)
    return app.logger

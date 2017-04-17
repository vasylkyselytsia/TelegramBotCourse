import logging
from settings import dir_path

__all__ = ['logger', 'log']


logFormatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s]  %(message)s')
logger = logging.getLogger()

logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler('{0}/{1}.log'.format(dir_path + '/logs/', 'log_file'))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def log(message, status='info'):
    if hasattr(logger, status):
        function = getattr(logger, status)
        function('-' * 80)
        function(message)
        function('-' * 80)
    return

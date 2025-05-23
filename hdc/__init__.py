import logging

formatter = logging.Formatter('[%(asctime)s] %(filename)15s[line:%(lineno)4d] \
                              [%(levelname)s] %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('HDC')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


__all__ = ['logger']
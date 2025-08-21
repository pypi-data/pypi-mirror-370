import logging

def get_logger(name, file_path=None):

    logger = logging.getLogger(name)
    if file_path:
        fh = logging.FileHandler('{}.log'.format(file_path))
    else:
        fh = logging.StreamHandler()
    fh_formatter = logging.Formatter('%(asctime)s [%(filename)s:%(funcName)s] %(message)s', "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)

    return logger

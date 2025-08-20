import logging as lg


logger = lg.getLogger('botobuddy')


def setup_logging(verbose):
    logger.setLevel(lg.INFO if not verbose else lg.DEBUG)

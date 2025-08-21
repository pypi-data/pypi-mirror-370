import logging

logging.basicConfig(format="[%(levelname)-8s][%(asctime)s] %(message)s")
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.CRITICAL)

def set_level(verbose, debug):
    """
    set_level - Set the log level
    """
    if verbose:
        Logger.setLevel(logging.INFO)
    if debug:
        Logger.setLevel(logging.DEBUG)

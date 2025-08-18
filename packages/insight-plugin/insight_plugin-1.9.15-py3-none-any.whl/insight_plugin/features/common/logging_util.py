import logging
import sys


class BaseLoggingFeature:
    BASE = None

    def __init__(self, name=None, verbose=False):
        if name is None:
            name = self.__class__.__name__
        if BaseLoggingFeature.BASE is None:
            BaseLoggingFeature.setup(verbose)
        self.logger = logging.getLogger(name)

    # TODO: Find usages of this and safely remove
    def set_log_level(self, verbose: bool):
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    @staticmethod
    def setup(verbose: bool):
        # Set up base logger and log output for all inheriting loggers
        _LOGGER = logging.getLogger()
        if verbose:
            _LOGGER.setLevel(logging.DEBUG)
        else:
            _LOGGER.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
        # print to standard out
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        _LOGGER.addHandler(handler)
        # Set the base feature for later
        BaseLoggingFeature.BASE = _LOGGER

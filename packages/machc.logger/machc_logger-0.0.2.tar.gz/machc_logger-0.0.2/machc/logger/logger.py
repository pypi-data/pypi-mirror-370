import logging
from typing import Any

from machc.configurator.configurator import Configurator


class Logger:

    def __init__(self):
        self.debug = None
        self.provider = None
        pass

    def init(self, configurator: Configurator = None, provider=None):
        self.debug = False
        if provider:
            self.provider = provider
        else:
            self.provider = logging

        self.debug = configurator.get_boolean("log.debug") if configurator else False
        if hasattr(self.provider, 'basicConfig'):
            level = logging.DEBUG if self.debug else logging.INFO
            self.provider.basicConfig(level=level)
        else:
            level = "DEBUG" if self.debug else "INFO"
            self.provider.setLevel("DEBUG")


class Log():
    def __init__(self, name: str):
        """
        Initializes the Logger instance for a given name.
        Retrieves the log level from the configuration for the logger or falls back to the root level.
        """
        self.name = name
        self.__log = logger.provider

    def _get_log(self):
        if not self.__log:
            provider = logger.provider
            if provider:
                if hasattr(provider, 'getLogger'):
                    self.__log = provider.getLogger(self.name)
                    if self.debug:
                        self.__log.setLevel(logging.DEBUG)
                    else:
                        self.__log.setLevel(logging.INFO)
                else:
                    self.__log = provider
        return self.__log

    def debug(self, *args: Any):
        """
        Logs debug messages if the log level permits it.
        """
        # if self.is_log_debug():
        log = self._get_log()
        if log:
            log.debug(args)
        else:
            print(args)

    def info(self, *args: Any):
        """
        Logs info messages if the log level permits it.
        """
        # if self.is_log_info():
        log = self._get_log()
        if log:
            log.info(args)
        else:
            print(args)

    def warning(self, *args: Any):
        """
        Logs warning messages if the log level permits it.
        """
        # if self.is_log_warning():
        log = self._get_log()
        if log:
            log.warning(args)
        else:
            print(args)

    def error(self, *args: Any):
        """
        Logs error messages regardless of the log level.
        """
        log = self._get_log()
        if log:
            log.error(args)
        else:
            print(args)


logger = Logger()

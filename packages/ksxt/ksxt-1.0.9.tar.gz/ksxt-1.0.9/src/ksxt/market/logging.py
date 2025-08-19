import logging


default_logger = logging.getLogger("")
default_logger.level = logging.INFO


class KsxtLogger:
    logger: logging.Logger = default_logger

    def _logger_ready(self, logger: logging.Logger):
        pass

    def _emit_logger(self, logger: logging.Logger = None):
        if logger:
            n = logger != getattr(self, "logger", None)
            self.logger = logger
        else:
            self.logger = default_logger
            n = True

        for obj in self.__dict__.values():
            if isinstance(obj, KsxtLogger):
                obj._emit_logger(self.logger)

        if n:
            self._logger_ready(logger)  # type: ignore

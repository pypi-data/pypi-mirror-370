class BaseError(Exception):
    pass


class ExchangeError(BaseError):
    pass


class NotSupportedError(ExchangeError):
    pass

class CurrencyConversionException(Exception):
    """
    Raised by conversion utility function when problems arise
    """


class RateBackendError(Exception):
    """
    Base exceptions raised by RateBackend implementations
    """

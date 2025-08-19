class Error(Exception):
    pass


class InitializationError(Error):
    pass


class UnsupportedFeatureError(Error):
    pass


class InProgressError(Error):
    pass


class IncompleteMessageError(Error):
    pass

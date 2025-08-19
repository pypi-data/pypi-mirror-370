from .devv_error import DevvError


class InvalidEndpointError(DevvError):
    pass


class InvalidValueError(DevvError):
    pass


class DuplicateRecipeError(InvalidValueError):
    def __init__(self):
        super().__init__("This recipe already exists.", "name", 1010)


class TXFailedError(DevvError):
    pass


class MintFailedError(TXFailedError):
    pass


class CoreTimeoutError(DevvError):
    pass

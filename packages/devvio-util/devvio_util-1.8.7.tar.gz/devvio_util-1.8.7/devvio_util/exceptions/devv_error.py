class DevvError(Exception):
    def __init__(
        self, message, errobj="", code=None, debug="", endpoint="unknown"
    ) -> None:
        self._message = message
        self._endpoint = endpoint
        self._errobj = errobj
        self._code = code
        self._debug = debug

    def __str__(self):
        message = (
            f"{self.__class__.__name__}: {self.message()};"
            f"errobj({self.object()});"
            f"code({self.code()});"
            f"debug({self.debug()})"
        )

        return message

    def message(self):
        return self._message

    def object(self):
        return self._errobj

    def code(self):
        return self._code

    def debug(self):
        return self._debug

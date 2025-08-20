class MalformedResultsException(Exception):
    message: str
    error_code: int

    def __init__(self, msg: str, err_code: int = 10) -> None:
        super().__init__(msg)
        self.message = msg
        self.error_code = err_code

    def __str__(self) -> str:
        return f"Error {self.error_code}: {self.message}"

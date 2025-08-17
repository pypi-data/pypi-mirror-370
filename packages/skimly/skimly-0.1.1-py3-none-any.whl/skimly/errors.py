class SkimlyError(Exception):
    def __init__(self, message: str, status: int = 500, code: str | None = None, data=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.data = data

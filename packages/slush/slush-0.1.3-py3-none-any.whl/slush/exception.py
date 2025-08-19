from slush.core.exception import HTTPBaseException

class NotFound(HTTPBaseException):
    def __init__(self, detail="Not Found"):
        super().__init__(404, detail)


class MethodNotAllowed(HTTPBaseException):
    def __init__(self, detail="Method Not Allowed", allowed_methods=None):
        headers = [("Content-Type", "application/json")]
        if allowed_methods:
            headers.append(("Allow", ", ".join(allowed_methods)))
        super().__init__(405, detail, headers)


class BadRequest(HTTPBaseException):
    def __init__(self, detail="Bad Request"):
        super().__init__(400, detail)


class InternalServerError(HTTPBaseException):
    def __init__(self, detail="Internal Server Error"):
        super().__init__(500, detail)


class ValidationError(HTTPBaseException):
    def __init__(self, detail="Validation Error"):
        super().__init__(422, detail)
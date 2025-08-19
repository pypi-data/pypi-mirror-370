# core/exceptions.py

class HTTPBaseException(Exception):
    def __init__(self, status_code: int, detail: str = "", headers=None):
        self.status_code = status_code
        self.detail = detail or self.default_detail()
        self.headers = headers or [("Content-Type", "application/json")]

    def default_detail(self):
        return "An error occurred"

    def as_response(self):
        from slush.core.response import Response
        return Response(
            body={"error": self.detail},
            status=f"{self.status_code} {self.status_text()}",
            headers=self.headers
        )

    def status_text(self):
        return {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }.get(self.status_code, "Unknown Error")

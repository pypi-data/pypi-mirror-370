import json
from slush.const import STATUS_PHRASES

class Response:
    def __init__(self, body="", status=200, headers=None, content_type=None):
        self.headers = headers or []
        self._cookies = []

        if isinstance(status, str) and status.isdigit():
            status = int(status)

        if isinstance(status, int):
            phrase = STATUS_PHRASES.get(status, "OK")
            self.status = f"{status} {phrase}"
        else:
            self.status = status

        # Content type inference
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
            content_type = content_type or "application/json"
        elif isinstance(body, str):
            content_type = content_type or "text/plain"
        else:
            content_type = content_type or "application/octet-stream"

        if isinstance(body, str):
            body = body.encode("utf-8")

        self.body = body
        if content_type is not None:
            self.set_header("Content-Type", content_type)   

    def set_header(self, key, value):
        self.headers = [h for h in self.headers if h[0].lower() != key.lower()]
        self.headers.append((key, value))

    def set_cookie(self, key, value, path="/", httponly=True, max_age=None):
        cookie = f"{key}={value}; Path={path}"
        if httponly:
            cookie += "; HttpOnly"
        if max_age is not None:
            cookie += f"; Max-Age={max_age}"
        self._cookies.append(("Set-Cookie", cookie))

    def finalize(self):
        if not isinstance(self.body, bytes):
            self.body = str(self.body).encode("utf-8")
        return self.status, self.headers + self._cookies, [self.body]

    @classmethod
    def json(cls, data, status=200, headers=None):
        body = json.dumps(data)
        return cls(body=body, status=status, headers=headers, content_type="application/json")

    @classmethod
    def text(cls, data, status=200, headers=None):
        return cls(body=data, status=status, headers=headers, content_type="text/plain")

    @classmethod
    def html(cls, data, status=200, headers=None):
        return cls(body=data, status=status, headers=headers, content_type="text/html")

    @classmethod
    def redirect(cls, location, status=302): 
        return cls(body=b"", status=status, headers=[("Location", location)], content_type=None)

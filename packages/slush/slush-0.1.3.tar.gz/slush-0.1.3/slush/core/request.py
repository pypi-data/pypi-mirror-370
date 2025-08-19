# core/request.py

import json
from urllib.parse import parse_qs
from cgi import FieldStorage
from typing import Optional
from slush.utils.files import UploadedFile


class Request:
    def __init__(self, environ: dict):
        """
        Initialize a Request object from WSGI environment.
        """
        self.environ = environ
        self.method = environ["REQUEST_METHOD"]
        self.path = environ["PATH_INFO"]
        self._body = None  # Lazy-loaded

        self.query_params = self._parse_query()
        self.headers = self._parse_headers()
        self.cookies = self._parse_cookies()

    def _parse_query(self) -> dict:
        raw_query = self.environ.get("QUERY_STRING", "")
        return {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(raw_query).items()
        }

    def _parse_headers(self) -> dict:
        headers = {}
        for key, value in self.environ.items():
            if key.startswith("HTTP_"):
                header = key[5:].replace("_", "-").title()
                headers[header] = value
        if "CONTENT_TYPE" in self.environ:
            headers["Content-Type"] = self.environ["CONTENT_TYPE"]
        if "CONTENT_LENGTH" in self.environ:
            headers["Content-Length"] = self.environ["CONTENT_LENGTH"]
        return headers

    def _parse_cookies(self) -> dict:
        cookie_str = self.environ.get("HTTP_COOKIE", "")
        cookies = {}
        for pair in cookie_str.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                cookies[k] = v
        return cookies

    def _read_body(self) -> str:
        if self._body is None:
            try:
                length = int(self.environ.get("CONTENT_LENGTH", 0))
            except (ValueError, TypeError):
                length = 0
            self._body = (
                self.environ["wsgi.input"].read(length).decode("utf-8")
                if length > 0
                else ""
            )
        return self._body

    @property
    def body(self) -> str:
        return self._read_body()

    def json(self) -> Optional[dict]:
        try:
            return json.loads(self._read_body())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def form(self) -> dict:
        self._parse_form_data()
        return {
            key: fs.getvalue()
            for key, fs in self._form_data.items()
            if not isinstance(fs, FieldStorage) or not fs.filename
        }

    def files(self) -> dict:
        self._parse_form_data()
        return {
            key: UploadedFile(fs)
            for key, fs in self._form_data.items()
            if isinstance(fs, FieldStorage) and fs.filename
        }

    def _parse_form_data(self):
        if hasattr(self, "_form_data"):
            return  # already parsed

        self._form_data = {}
        try:
            fs = FieldStorage(
                fp=self.environ["wsgi.input"],
                environ=self.environ,
                keep_blank_values=True
            )
            for key in fs:
                self._form_data[key] = fs[key]
        except Exception:
            self._form_data = {}
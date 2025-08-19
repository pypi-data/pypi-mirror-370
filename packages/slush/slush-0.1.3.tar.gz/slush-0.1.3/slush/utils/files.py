import os
from cgi import FieldStorage, MiniFieldStorage
from slush.exception import InternalServerError
from typing import Optional, BinaryIO
from slush.settings import Config

class UploadedFile:
    def __init__(self, field: FieldStorage):
        self.filename: str = field.filename
        self.content_type: str = field.type
        self.file: BinaryIO = field.file
        self.size: int = self._get_file_size()

    def _get_file_size(self) -> int:
        current_pos = self.file.tell()
        self.file.seek(0, 2)  # Seek to end
        size = self.file.tell()
        self.file.seek(current_pos)  # Return to original position
        return size

    def read(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def save(self, path: Optional[str] = None) -> str:
        config = Config()
        directory = path or config.get("upload_dir", "./uploads")
        os.makedirs(directory, exist_ok=True)

        if not self.filename:
            raise InternalServerError("No filename provided for the uploaded file.")

        file_path = os.path.join(directory, self.filename)
        with open(file_path, "wb") as f:
            f.write(self.read())

        return file_path
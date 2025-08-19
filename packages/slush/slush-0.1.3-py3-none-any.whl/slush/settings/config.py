from typing import Optional
from slush.meta import SingletonMeta


class Config(metaclass=SingletonMeta):
    def __init__(self, **kwargs):
        # Defaults
        self.debug = True
        self.upload_dir = "./uploads"

        for key, value in kwargs.items():
            setattr(self, key, value)

    def set(self, key: str, value):
        setattr(self, key, value)

    def get(self, key: str, default=None):
        return getattr(self, key, default)

    def __repr__(self):
        return f"<Config: {self.__dict__}>"

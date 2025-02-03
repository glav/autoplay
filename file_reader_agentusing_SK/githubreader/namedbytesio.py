import io
from typing import TypeAlias

from typing_extensions import Buffer

ReadableBuffer: TypeAlias = Buffer


class NamedBytesIO(io.BytesIO):
    def __init__(self, name: str = None, initial_bytes: ReadableBuffer = None):
        if initial_bytes is None:
            super().__init__()
        else:
            super().__init__(initial_bytes)
        self.name = name

from pathlib import Path


class RawResource:

    def __init__(self, data: bytes):
        self.data = data

    @staticmethod
    def from_file(file_path: Path):
        return RawResource(file_path.read_bytes())

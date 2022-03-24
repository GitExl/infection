import struct
import wave
from pathlib import Path


class SoundResource:

    def __init__(self, sample_rate: int, channels: int, bit_depth: int, data: bytes):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.data = data

    @staticmethod
    def from_doom_sound(data: bytes):
        _fmt, sample_rate, length = struct.unpack_from('<HHI', data)
        length -= 32

        return SoundResource(
            sample_rate,
            1,
            8,
            data[24:-16]
        )

    @staticmethod
    def from_wave_file(file_path: Path):
        with wave.open(file_path.as_posix(), 'rb') as wav:
            return SoundResource(
                wav.getframerate(),
                wav.getnchannels(),
                wav.getsampwidth() * 8,
                wav.readframes(wav.getnframes())
            )

    def getdata(self) -> bytes:
        header = struct.pack('<HHI', 3, self.sample_rate, len(self.data) + 32)
        return header + bytes([self.data[0]] * 16) + self.data + bytes([self.data[-1]] * 16)

from io import BytesIO
from _io import BufferedReader
from devvio_util.primitives.devv_constants import (
    kUINT64_SIZE,
    kUINT32_SIZE,
    kUINT_SIZE,
    kMERKLE_SIZE,
    kPREV_HASH_SIZE,
)


class InputBuffer:
    """
    Utilizes a BytesIO stream to parse various useful types.
    Can be instantiated with a filepath, bytes object, or BytesIO object.
    If used in a 'with' statement, will clean itself up upon exit.
    """

    def __init__(self, file: str or bytes or BytesIO):
        if isinstance(file, str):
            self._reader = BytesIO(open(file, "rb").read())
        elif isinstance(file, bytes):
            self._reader = BytesIO(file)
        elif isinstance(file, BytesIO):
            self._reader = file
        elif isinstance(file, BufferedReader):
            self._reader = BytesIO(file.read())
        else:
            raise RuntimeError(
                f"Invalid InputBuffer: need bytes, filepath, BytesIO, or BufferedReader\
                 (given {type(file)})"
            )
        self._size = len(self._reader.read())
        self._reader.seek(0)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._reader.__exit__()

    def __sizeof__(self) -> int:
        return self._size

    def __getitem__(self, index: tuple) -> bytes:
        offset, num_bytes = index
        return self.get_bytes(offset, num_bytes)

    def get_next_uint64(self, increment: bool = True) -> int:
        return self.get_next_int(kUINT64_SIZE, increment)

    def get_next_int64(self, increment: bool = True) -> int:
        return self.get_next_int(kUINT64_SIZE, increment, signed=True)

    def get_next_uint32(self, increment: bool = True) -> int:
        return self.get_next_int(kUINT32_SIZE, increment)

    def get_next_uint8(self, increment: bool = True) -> int:
        return self.get_next_int(kUINT_SIZE, increment)

    def get_next_merkle(self, increment: bool = True) -> str:
        return self.get_next_hex(kMERKLE_SIZE, increment)

    def get_next_prev_hash(self, increment: bool = True) -> str:
        return self.get_next_hex(kPREV_HASH_SIZE, increment)

    def get_next_hex(self, num_bytes: int, increment: bool = True) -> str:
        result = self.get_next_bytes(num_bytes, increment).hex()
        return result

    def get_next_int(
        self,
        num_bytes: int,
        increment: bool = True,
        signed: bool = False,
    ) -> int:
        result = get_int(self.get_next_bytes(num_bytes, increment), signed)
        return result

    def get_next_prefixed_obj(self, increment: bool = True) -> bytes:
        offset = self.tell()
        size = self.get_next_uint8()
        res = self.get_next_bytes(size)
        if not res or not increment:
            self.seek(offset)
        return res

    def get_next_bytes(self, num_bytes: int, increment: bool = True) -> bytes:
        result = self._reader.read(num_bytes)
        if not increment:
            self._reader.seek(self._reader.tell() - num_bytes)
        return result

    def get_bytes(self, offset: int, num_bytes: int) -> bytes:
        curr_offset = self._reader.tell()
        self._reader.seek(offset)
        result = self.get_next_bytes(num_bytes, False)
        self._reader.seek(curr_offset)
        return result

    def get_int(self, offset: int, num_bytes: int) -> int:
        curr_offset = self._reader.tell()
        self._reader.seek(offset)
        result = self.get_next_int(num_bytes, False)
        self._reader.seek(curr_offset)
        return result

    def seek(self, offset: int):
        self._reader.seek(offset)

    def tell(self) -> int:
        return self._reader.tell()

    def read(self, size: int = -1):
        return self._reader.read(size)


def get_int(x: bytes, signed: bool) -> int:
    return int.from_bytes(x, "little", signed=signed)


def set_uint64(x: int) -> bytes:
    return set_int(x, kUINT64_SIZE, False)


def set_uint32(x: int) -> bytes:
    return set_int(x, kUINT32_SIZE, False)


def set_int64(x: int) -> bytes:
    return set_int(x, kUINT64_SIZE, True)


def set_uint8(x: int) -> bytes:
    return set_int(x, kUINT_SIZE, False)


def set_int(x: int, num_bytes: int, signed: bool) -> bytes:
    return x.to_bytes(num_bytes, "little", signed=signed)


def is_hex(s: str) -> bool:
    return not set(s) - set("abcdefABCDEF0123456789")

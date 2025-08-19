from devvio_util.primitives.summary import Summary
from devvio_util.primitives.transaction import Transaction
from devvio_util.primitives.utils import InputBuffer
from devvio_util.primitives.validation import Validation
from devvio_util.primitives.chainstate import Chainstate
from devvio_util.primitives.devv_constants import VALID_BLOCK_VERSIONS


class FinalBlock:
    """
    Parses and holds FinalBlock data given either a filepath or an InputBuffer holding block binary.
    If given an InputBuffer, the block will seek to the beginning before starting to parse.
    """

    def __init__(self, final_blk: InputBuffer or str, prior: Chainstate = None):
        """
        Initializes a FinalBlock, given either a filepath or an InputBuffer holding block binary.
        If given an InputBuffer, the block will seek to the beginning before starting to parse.
        :param final_blk: block binary, given by a filepath string or an InputBuffer
        :param prior: optional Chainstate object to be updated with this block's transactions
        :type: prior: Chainstate
        """
        self._canonical = None
        if isinstance(final_blk, str):
            self._canonical = InputBuffer(final_blk)
        self._shard_index = None
        self._block_height = None
        self._block_time = None
        self._prev_hash = None
        self._merkle = None
        self._summary = None
        self._tx_size = None
        self._sum_size = None
        self._val_count = None
        self._vals = None
        self._version = None
        self._is_legacy = None
        self._txs = []

        if final_blk and isinstance(final_blk, InputBuffer):
            self.from_buffer(final_blk, prior)
        elif self._canonical:
            self.from_buffer(self._canonical, prior)
        else:
            raise RuntimeError(f"Invalid FinalBlock: input type {type(final_blk)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._canonical:
            self._canonical.__exit__()

    def get_indexes(self, buffer: InputBuffer):
        self._version = buffer.get_next_uint8()
        if not self._version:
            raise RuntimeError("Invalid FinalBlock: buffer empty!")

        if self._version not in VALID_BLOCK_VERSIONS:
            raise RuntimeError(f"Invalid FinalBlock: bad {self._version}")

        self._is_legacy = self._version == 0
        num_bytes_ = buffer.get_next_uint64()
        if not num_bytes_:
            raise RuntimeError("Invalid FinalBlock: wrong size!")

        if not self._is_legacy:
            self._shard_index = buffer.get_next_uint64()
            self._block_height = buffer.get_next_uint64()

        self._block_time = buffer.get_next_uint64()
        self._prev_hash = buffer.get_next_prev_hash()
        self._merkle = buffer.get_next_merkle()

        self._tx_size = buffer.get_next_uint64()
        self._sum_size = buffer.get_next_uint64()
        self._val_count = buffer.get_next_uint32()

    def from_buffer(self, buffer: InputBuffer, prior: Chainstate = None):
        # Back to begin
        buffer.seek(0)
        self.get_indexes(buffer)

        tx_start = buffer.tell()

        while buffer.tell() < tx_start + self._tx_size:
            one_tx = Transaction(buffer, self._is_legacy)
            self._txs.append(one_tx)

        self._summary = Summary(buffer)
        if prior:
            prior.update(self._summary)
        self._vals = Validation(buffer)

    def __bool__(self):
        return self._block_height is not None

    def get_shard_index(self) -> int:
        return self._shard_index

    def get_block_height(self) -> int:
        return self._block_height

    def get_block_time(self) -> int:
        return self._block_time

    def get_tx_size(self) -> int:
        return self._tx_size

    def get_sum_size(self) -> int:
        return self._sum_size

    def get_val_count(self) -> int:
        return self._val_count

    def get_validation(self) -> Validation:
        return self._vals

    def get_summary(self) -> Summary:
        return self._summary

    def get_txs(self) -> list:
        return self._txs

    def get_version(self) -> int:
        return self._version

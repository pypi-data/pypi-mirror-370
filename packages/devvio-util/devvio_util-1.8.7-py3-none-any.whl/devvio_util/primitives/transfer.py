from devvio_util.primitives.devv_constants import kTRANSFER_NONADDR_DATA_SIZE
from devvio_util.primitives.address import Address
from devvio_util.primitives.utils import InputBuffer, set_int64, set_uint64


class Transfer:
    """
    A Transfer represents one component of a Transaction and consists
    of an address, coin id, amount and delay. Can be initialized from a dictionary, byte array, or InputBuffer
    """

    def __init__(self, xfer: dict or bytes or InputBuffer or None = None):
        """
        Initialize a Transfer with a dictionary, bytes object, or InputBuffer.
        If given an InputBuffer, building a Transfer will increment the cursor from its current index.
        :param xfer: a dict, bytes, or InputBuffer containing the Transfer binary
        """
        self._addr = None
        self._delay = None
        self._amount = None
        self._coin_id = None
        self._canonical = None
        self._size = 0
        if isinstance(xfer, bytes):
            self.from_canonical(xfer)
        if isinstance(xfer, InputBuffer):
            self.from_buffer(xfer)
        elif isinstance(xfer, dict):
            self.from_dict(xfer)
        elif xfer is not None:
            raise ValueError(
                f"Invalid Transfer: could not initialize from {type(xfer)}"
            )

    def from_canonical(self, xfer_bin: bytes):
        """
        Initialize a Transfer from a bytes object.
        """
        self._canonical = None
        buffer = InputBuffer(xfer_bin)
        self.from_buffer(buffer)

    def from_buffer(self, buffer: InputBuffer):
        """
        Initialize a Transfer from an InputBuffer.
        """
        self._canonical = None
        buffer_index = buffer.tell()
        addr_size = buffer.get_next_uint8()
        addr_bin = buffer.get_next_bytes(addr_size)
        if not addr_bin:
            raise RuntimeError("Invalid Transfer: buffer EOF")
        self._addr = Address(addr_bin)
        self._size = addr_size + kTRANSFER_NONADDR_DATA_SIZE
        self._canonical = buffer.get_bytes(buffer_index, self._size)
        if not self._canonical:
            raise RuntimeError("Invalid Transfer: buffer too small")
        self._coin_id = buffer.get_next_uint64()
        self._amount = buffer.get_next_int64()
        self._delay = buffer.get_next_uint64()

    def set_canonical(self):
        """
        Build binary representation from the stored attributes.
        """
        if not isinstance(self._amount, int):
            raise ValueError("Invalid Transfer: invalid amount")
        if not isinstance(self._delay, int):
            raise ValueError("Invalid Transfer: invalid delay")
        if not isinstance(self._coin_id, int):
            raise ValueError(f"Invalid Transfer: invalid coin_id {self._coin_id}")
        if isinstance(self._addr, str):
            self._addr = Address(self._addr)
        if not isinstance(self._addr, Address):
            raise ValueError("Invalid Transfer: invalid Address")
        self._canonical = bytes()
        self._size = self._addr.get_size() + kTRANSFER_NONADDR_DATA_SIZE
        self._canonical += self._addr.get_canonical()
        self._canonical += set_uint64(self._coin_id)
        self._canonical += set_int64(self._amount)
        self._canonical += set_uint64(self._delay)
        if len(self._canonical) != self._size + 1:
            raise RuntimeError(
                f"Invalid Transfer: canonical size invalid ({len(self._canonical)} != {self._size + 1})"
            )

    def __bool__(self) -> bool:
        return self._canonical is not None

    def __str__(self) -> str:
        return str(self.get_dict())

    def get_dict(self) -> dict:
        """
        Return dictionary representation of Transfer with amount, delay, coin id, and address (as hex string).
        (warning: hex string representation of Address will not include size prefix)
        :return: contains keys "amount", "delay", "coin", and "address"
        :rtype: dict
        """
        res = {
            "amount": self._amount,
            "delay": self._delay,
            "coin": self._coin_id,
            "address": str(self._addr),
        }
        return res

    def get_coin(self) -> int:
        """
        Return Transfer coin id as integer.
        :return: coin id
        :rtype: int
        """
        return self._coin_id

    def get_addr(self) -> Address:
        """
        Return this Transfer's wallet address
        :return: Transfer address
        :rtype: Address
        """
        return self._addr

    def get_addr_str(self) -> str:
        """
        Return this Transfer's wallet address as a hex string
        (warning: this won't include size prefix)
        :return: Transfer address
        :rtype: str
        """
        return str(self._addr)

    def get_amount(self) -> int:
        """
        Return Transfer amount
        :return: amount
        :rtype: int
        """
        return self._amount

    def get_delay(self) -> int:
        """
        Return Transfer delay
        :return: delay
        :rtype: int
        """
        return self._delay

    def get_size(self) -> int:
        """
        Return Transfer size, in number of bytes
        :return: size
        :rtype: int
        """
        return self._size

    def get_canonical(self) -> bytes:
        """
        Return Transfer binary representation.
        :return: Transfer canonical
        :rtype: bytes
        """
        return self._canonical

    def to_dict(self) -> dict:
        """
        Return Transfer dictionary representation. (contains Address object)
        :return: Transfer dictionary
        :rtype: dict
        """
        dict_transfer = dict()
        dict_transfer["address"] = self.get_addr()
        dict_transfer["amount"] = self.get_amount()
        dict_transfer["coin"] = self.get_coin()
        dict_transfer["delay"] = self.get_delay()
        return dict_transfer

    def from_dict(self, xfer_dict: dict):
        """
        Initialize Transfer from dictionary representation.
        :param xfer_dict: dict holding delay, coin, amount, and address
        :type xfer_dict: dict
        """
        self._delay = xfer_dict.get("delay")
        self._coin_id = xfer_dict.get("coin")
        self._amount = xfer_dict.get("amount")
        addr = xfer_dict.get("address")
        if isinstance(addr, str):
            self._addr = Address(addr)
        if isinstance(addr, Address):
            self._addr = addr
        self.set_canonical()

    @staticmethod
    def get_xfers_from_buffer(buffer: InputBuffer, offset: int, num_bytes: int) -> list:
        """
        Returns list of Transfers from InputBuffer, and increments buffer cursor
        :param buffer: buffer holding binary list of Transfer objects, often as a part of a Transaction
        :type buffer: InputBuffer
        :param offset: starting point for the list of Transfer objects within the InputBuffer
        :type offset: int
        :param num_bytes: number of total bytes in the list of Transfers
        :type num_bytes: int
        :return: list of Transfers
        :rtype: list
        """
        xfers = []
        buffer.seek(offset)
        while buffer.tell() < offset + num_bytes:
            xfers.append(Transfer(buffer))
        return xfers

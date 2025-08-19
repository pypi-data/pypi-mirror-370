from devvio_util.primitives.devv_constants import (
    kNODE_ADDR_SIZE,
    kWALLET_ADDR_SIZE,
    kWALLET_ADDR_BUF_SIZE,
    kNODE_ADDR_BUF_SIZE,
    kWALLET_SIG_BUF_SIZE,
    kNODE_SIG_BUF_SIZE,
)
from devvio_util.primitives.utils import InputBuffer, is_hex


class Address:
    """
    Addresses are wrappers for EC public keys that lie on either SECP256K1 or SECP384R1 curves for wallets or nodes,
    respectively.
    They contain a 1-byte prefix indicating address length, which is used to differentiate these two key types.
    """

    def __init__(self, addr: str or bytes or InputBuffer = None):
        self._canonical = None
        self._size = None
        self.set_addr(addr)

    def set_addr(self, addr: str or bytes or InputBuffer):
        if not addr:
            raise ValueError("Invalid Address: no bytes or string given")
        if isinstance(addr, str):
            if not is_hex(addr):
                raise ValueError(f"Invalid Address: not a valid hex string ({addr})")
            addr_bin = bytes.fromhex(addr)
        elif isinstance(addr, bytes):
            addr_bin = addr
        elif isinstance(addr, InputBuffer):
            addr_bin = addr.get_next_prefixed_obj()
        else:
            raise ValueError(
                f"Invalid Address: cannot initialize from type {type(addr)}"
            )
        if not addr_bin:
            return None
        self._size = len(addr_bin)
        if self._size == kWALLET_ADDR_SIZE or self._size == kNODE_ADDR_SIZE:
            self._canonical = bytes([self._size]) + addr_bin
        elif self._size != (prefix_size := addr_bin[0] + 1):
            raise RuntimeError(
                f"Invalid Address: prefix != num bytes given ({prefix_size} != {self._size})"
            )
        elif self._size == kWALLET_ADDR_BUF_SIZE or self._size == kNODE_ADDR_BUF_SIZE:
            self._canonical = addr_bin
            self._size -= 1
        else:
            raise ValueError(f"Invalid Address: invalid size {self._size}")

    def __eq__(self, other) -> bool:
        """
        Compare addresses. True if address binaries are equivalent.
        """
        return self._canonical == other.get_canonical()

    def __bool__(self) -> bool:
        """
        Evaluate as boolean, serves as isNull()
        """
        return self._canonical is not None

    def __str__(self) -> str:
        """
        Get formatted address. Excludes the 1-byte size prefix.
        :return: address as hex string
        :rtype: str
        """
        return self.get_hex_str()

    def __len__(self) -> int:
        """
        Get address length. Excludes the 1-byte size prefix.
        :return: size of address
        :rtype: int
        """
        return self.get_size()

    def get_size(self) -> int:
        """
        Get address length. Excludes the 1-byte size prefix.
        :return: size of address
        :rtype: int
        """
        return self._size

    def get_canonical(self, legacy: bool = False) -> bytes:
        """
        Get address binary. If legacy = True, this will exclude the 1-byte size prefix.
        :param legacy:
        :type legacy: bool
        :return: address binary
        :rtype: bytes
        """
        if legacy:
            return self._canonical[1:]
        return self._canonical

    def get_hex_str(self) -> str:
        """
        Get formatted address. Excludes the 1-byte size prefix.
        :return: address as hex string
        :rtype: str
        """
        if not self._canonical:
            raise RuntimeError("Address is not initialized!")
        return self._canonical.hex()[2:].upper()

    def is_wallet_addr(self) -> bool:
        """
        Check if address corresponds to a wallet. Wallet addresses lie on the SECP256K1 curve
        :return: True if address is on the SECP256K1 curve
        :rtype: bool
        """
        if not self:
            return False
        return self._size == kWALLET_ADDR_SIZE

    def is_node_addr(self) -> bool:
        """
        Check if address corresponds to a node. Node addresses lie on the SECP384R1 curve
        :return: True if address is on the SECP384R1 curve.
        :rtype: bool
        """
        if not self:
            return False
        return self._size == kNODE_ADDR_SIZE

    def get_corresponding_sig_size(self) -> int:
        """
        Return the length (including the 1-byte size prefix) of a signature generated from the given address.
        :return: Length of corresponding signature
        :rtype: int
        """
        if self.is_wallet_addr():
            return kWALLET_SIG_BUF_SIZE
        elif self.is_node_addr():
            return kNODE_SIG_BUF_SIZE
        else:
            return 0

    @staticmethod
    def is_valid_addr_size(addr_size: int) -> bool:
        """
        Return true is the given length is valid for either node or wallet addresses.
        :param addr_size: a hypothetical address length
        :type addr_size: int
        :return: True if addr_size is valid
        :rtype: bool
        """
        return addr_size in [
            kWALLET_ADDR_SIZE,
            kWALLET_ADDR_BUF_SIZE,
            kNODE_ADDR_SIZE,
            kNODE_ADDR_BUF_SIZE,
        ]

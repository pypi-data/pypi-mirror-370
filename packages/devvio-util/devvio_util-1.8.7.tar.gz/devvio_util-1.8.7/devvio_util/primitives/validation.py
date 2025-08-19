from devvio_util.primitives.utils import InputBuffer
from devvio_util.primitives.address import Address
from devvio_util.primitives.signature import Signature
from devvio_util.primitives.devv_constants import (
    kNODE_ADDR_BUF_SIZE,
    kNODE_SIG_BUF_SIZE,
    kNODE_ADDR_SIZE,
    kNODE_SIG_SIZE,
)


class Validation:
    """
    Builds/stores a map of signer/Signature pairs for a Finalblock.
    """

    def __init__(self, buffer: InputBuffer, count: int = None):
        """
        Initialize the validation map.
        :param buffer: stream of bytes containing the validation block
        :type buffer: InputBuffer
        :param count: number of Address/Signature pairs in the given buffer; should equal the number of
        Transactions in a block
        :type count: int
        """
        self._raw_addrs = False
        self._sigs = {}

        remainder = count
        offset = buffer.tell()

        if remainder is not None:
            if offset + remainder * self.pair_size() > buffer.__sizeof__():
                raise RuntimeError(
                    f"Invalid Validation: buffer too small for {remainder} node addr/sig pairs"
                )
            while remainder > 0:
                self.add_pair_from_buffer(buffer)
                remainder = remainder - 1
        else:
            while self.add_pair_from_buffer(buffer):
                pass

    def add_pair_from_buffer(self, buffer: InputBuffer) -> bool:
        """
        Add an Address/Signature pair to this validation map from an InputBuffer.
        :param buffer: buffer containing the validation block
        :type buffer: InputBuffer
        :returns: Indicates a successful map update
        :rtype: bool
        """
        one_addr = Address(buffer)
        one_sig = Signature(buffer)
        if not (one_sig and one_addr):
            return False
        one_pair = {one_addr.get_hex_str(): one_sig}
        self._sigs.update(one_pair)
        return True

    def add_validation(self, address: Address, sig: Signature) -> bool:
        """
        Add an Address/Signature pair to this validation map.
        :param address: Address to add, will return False if this Address already exists in the validation map
        :type address: Address
        :param sig: Signature associated with the given Address
        :type sig: Signature
        :returns: Indicates a successful update
        :rtype: bool
        """
        if not address.is_node_addr():
            raise ValueError("Invalid Validation: Address must be a node Address")

        if not sig.is_node_sig():
            raise ValueError("Invalid Validation: Signature must be a node Signature")

        if self._sigs.get(address.get_hex_str()):
            return False

        self._sigs.update({address.get_hex_str(): sig})
        return True

    def add_validations(self, other) -> int:
        """
        Update this Validation with data from another.
        :param other: Validation object to pull data from
        :type other: Validation
        :returns: number of Validation pairs added
        :rtype: int
        """
        added = 0
        for address, sig in other.get_validation_map().items():
            if self.add_validation(address, sig):
                added += 1
        return added

    def get_first_validation(self) -> tuple:
        """
        Returns the first validation pair (Address, Signature)
        :returns: the validation map's first tuple; holds an Address as a hex string, and a Signature object
        :rtype: tuple
        """
        if not self._sigs:
            raise RuntimeError("Invalid Validation: sig map is empty")
        return next(iter(self._sigs.items()))

    def get_canonical(self) -> bytes:
        """
        Returns a byte vector representing this validation block.
        :return: a byte vector representing this validation block.
        :rtype: bytes
        """
        out = bytes()
        for addr, sig in self.get_validation_map().items():
            out += Address(addr).get_canonical()
            out += sig.get_canonical()
        return out

    def get_size(self) -> int:
        """
        Returns the size of this verification block in number of bytes
        :return: number of bytes for this verification block
        :rtype: int
        """
        return self.get_validation_count() * self.pair_size()

    def get_validation_count(self) -> int:
        """
        Returns the number of validations in this block.
        :return: number of validations in this block
        :rtype: int
        """
        return len(self._sigs)

    def pair_size(self) -> int:
        """
        Returns the number of bytes per validation pair (Address + Signature) in this block.
        If _raw_addrs is False (the default case), includes the size prefixes in the byte count.
        :return: number of bytes per validation in this block
        :rtype: int
        """
        if self._raw_addrs:
            return kNODE_ADDR_SIZE + kNODE_SIG_SIZE
        return kNODE_ADDR_BUF_SIZE + kNODE_SIG_BUF_SIZE

    def get_validation_map(self) -> dict:
        """
        Get the validation map.
        :returns: Validation map
        :rtype: dict
        """
        return self._sigs

    def set_raw_addrs(self, new_raw_addrs: bool):
        """
        Sets _raw_addrs, which is False by default.
        If _raw_addrs is False, includes the size prefixes in the byte count.
        """
        self._raw_addrs = new_raw_addrs

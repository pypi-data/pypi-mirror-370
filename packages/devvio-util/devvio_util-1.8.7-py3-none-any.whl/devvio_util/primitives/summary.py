from devvio_util.primitives.transfer import Transfer
from devvio_util.primitives.address import Address
from devvio_util.primitives.utils import InputBuffer, set_uint64, set_int64, set_uint32


class DelayedItem:
    """
    * Constructor
    * @param delay
    * @param delta
    """

    def __init__(self, delay_val: int = 0, delta_val: int = 0):
        self.delay = delay_val
        self.delta = delta_val

    def get_delay(self):
        return self.delay

    def get_delta(self):
        return self.delta


class Summary:
    """
    Holds a summary of block transactions that can be used to update verify sanity and update the chainstate.
    """

    def __init__(self, buffer: InputBuffer):
        self._summary_map = {}

        addr_count = buffer.get_next_uint32()
        for i in range(addr_count):
            addr_size = buffer.get_next_uint8()
            one_addr = Address(buffer.get_next_bytes(addr_size, increment=True))
            delayed = {}
            coin_map = {}
            delayed_count = buffer.get_next_uint64()
            coin_count = buffer.get_next_uint64()
            for j in range(delayed_count):
                coin = buffer.get_next_uint64()
                delay = buffer.get_next_uint64()
                delta = buffer.get_next_int64()
                delayed_item = DelayedItem(delay, delta)
                delayed[coin] = delayed_item

            for j in range(coin_count):
                coin = buffer.get_next_uint64()
                delta = buffer.get_next_int64()
                coin_map[coin] = delta

            self._summary_map[one_addr.get_hex_str()] = (
                delayed,
                coin_map,
            )  # TODO: validate this key 'get_hex_str'

    def get_map(self) -> dict:
        return self._summary_map

    def is_sane(self) -> bool:
        """
        Sanity check; returns true if no coins are lost or generated throughout a finalblock's transactions.
        :return: block sanity status
        :rtype: bool
        """
        if not self._summary_map:
            return False
        coin_total = 0
        for addr, summary_pair in self._summary_map.items():
            delayed_map = summary_pair[0]
            delta_map = summary_pair[1]
            for coin_id, delay_pair in delayed_map.items():
                coin_total += delay_pair.get_delta()
            for coin_id, delta in delta_map.items():
                coin_total += delta
        if coin_total != 0:
            print(f"Summary state invalid: {self.get_map()}")
            return False
        return True

    def get_xfers(self) -> list:
        """
        Returns a list of all transfers in a block
        :return: list of Transfer objects
        :rtype: Transfer
        """
        xfers = []
        for addr, summary_pair in self._summary_map.items():
            delayed_map = summary_pair[0]
            delta_map = summary_pair[1]
            for coin_id, delay_pair in delayed_map.items():
                one_xfer = {
                    "address": addr,
                    "coin": coin_id,
                    "amount": delay_pair.get_delta(),
                    "delay": delay_pair.get_delay(),
                }
                xfers.append(Transfer(one_xfer))
            for coin_id, delta in delta_map.items():
                one_xfer = {
                    "address": addr,
                    "coin": coin_id,
                    "amount": delta,
                    "delay": 0,
                }
                xfers.append(Transfer(one_xfer))
        return xfers

    def get_canonical(self) -> bytes:
        """
        Return binary representation of summary
        :return: summary binary
        :rtype: bytes
        """
        out = bytes()
        addr_count = len(self._summary_map)
        out += set_uint32(addr_count)
        for addr, pair in self._summary_map.items():
            out += Address(addr).get_canonical()
            delayed_map, coin_map = pair
            out += set_uint64(len(delayed_map))
            out += set_uint64(len(coin_map))
            for coin, xfer in delayed_map.items():
                out += set_uint64(coin)
                out += set_uint64(xfer.get_delay())
                out += set_int64(xfer.get_delta())
            for coin, delta in coin_map.items():
                out += set_uint64(coin)
                out += set_int64(delta)
        return out

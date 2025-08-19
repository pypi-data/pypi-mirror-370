from devvio_util.primitives.address import Address


class SmartCoin:
    """
    Simple struct to hold an Address, coinId, and amount
    """

    def __init__(self, addr: Address, coin: int, amount: int = 0):
        self._addr = addr
        self._coin = coin
        self._amount = amount

    def __bool__(self) -> bool:
        if not (self._addr and self._coin):
            return False
        return True

    def get_address(self) -> Address:
        return self._addr

    def get_coin(self) -> int:
        return self._coin

    def get_amount(self) -> int:
        return self._amount

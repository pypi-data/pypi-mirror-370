from devvio_util.primitives.devv_constants import kPROTOCOL_VERSION
from devvio_util.primitives.address import Address
from devvio_util.primitives.smart_coin import SmartCoin
from devvio_util.primitives.summary import Summary


class Chainstate:
    """
    Holds the state of the chain in the form of a map with wallet addresses as keys
    and lists of coin/balance pairs as values
    """

    def __init__(self):
        self._state_map = dict()

    def get_state_map(self) -> dict:
        """
        Returns the chainstate as a dictionary.
        :return: A map with wallet addresses as keys and lists of coin/balance pairs as values
        :rtype: dict
        """
        return self._state_map

    def get_amount(self, coin_id: int, addr: Address) -> int:
        """
        Returns the given wallet's balance for a coin.
        :param coin_id: request balance for this coin
        :type coin_id: int
        :param addr: the Address of the wallet to check
        :type addr: Address
        :return: the wallet's coin balance
        :rtype: int
        """
        addr_iter = self._state_map.get(addr.get_hex_str())
        if addr_iter:
            coin_map = addr_iter[1]
            coin_iter = coin_map[coin_id]
            if coin_iter:
                amount = coin_map[coin_id]
                return amount
        return 0

    def add_coin(self, coin: SmartCoin):
        """
        Updates a wallet's coin balance for this Chainstate
        :param coin: holds the coinId, Address, and amount to update the state map with
        :type coin: SmartCoin
        """
        it = self._state_map.get(coin.get_address().get_hex_str())
        if it and it.get(coin.get_coin()):
            it[coin.get_coin()] += coin.get_amount()
        elif it:
            it[coin.get_coin()] = coin.get_amount()
        else:
            inner = dict()
            inner[coin.get_coin()] = coin.get_amount()
            self._state_map[coin.get_address().get_hex_str()] = inner

    def update(self, summ: Summary):
        """
        Updates the Chainstate with a block's Summary
        :param summ: summary of transactions within a block
        :type summ: Summary
        """
        if not summ.is_sane():
            raise RuntimeError("Chainstate update failed: Summary is not sane")
        prev_state = self._state_map
        for xfer in summ.get_xfers():
            coin = SmartCoin(xfer.get_addr(), xfer.get_coin(), xfer.get_amount())
            try:
                self.add_coin(coin)
            except Exception as e:
                self._state_map = prev_state
                raise RuntimeError(
                    f"Failed to add SmartCoin to Chainstate: {e} "
                    f"(addr:{coin.get_address()}; coin:{coin.get_coin()}; amount:{coin.get_amount()})"
                )


class ChainCheckpoint:
    """
    Holds a snapshot of the chainstate
    """

    def __init__(self):
        self._version = kPROTOCOL_VERSION
        self._highest_block_hash = None
        self._chainstate_summary = None
        self._signer = None
        self._checkpoint_hash = None
        self._signature = None
        raise NotImplementedError

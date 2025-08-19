class Payload:
    """
    Parses and holds Payload data returned by the blockchain.
    """

    def __init__(self, payload_str: str):
        """
        Initializes a Payload, given a string representation of it.
        :param payload_str: a string representation of the payload returned by the blockchain.
        """
        if payload_str.count("<") < 4:
            raise ValueError(
                "Asset payload must be in the form of "
                "'VER<client_id<comment<root_sig<properties' -- {}".format(payload_str)
            )

        s = payload_str.split("<")
        self._asset_payload_ver = s[0] or None
        self._client_id = s[1] or None
        self._comment = s[2] or None
        self._root_sig = s[3] or None
        self._properties = "<".join(s[4:]) or {}

    def __repr__(self):
        payload_repr = (
            f"{self._asset_payload_ver}<{self._client_id}"
            f"<{self._comment}<{self._root_sig}<{self._properties}"
        )
        return payload_repr

    def get_ver(self):
        return self._asset_payload_ver

    def get_client_id(self):
        return self._client_id

    def get_comment(self):
        return self._comment

    def get_root_sig(self):
        return self._root_sig

    def get_properties(self):
        return self._properties

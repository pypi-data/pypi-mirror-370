from urllib.parse import quote_plus

import requests
import random
import time
from uuid import UUID, uuid4
from typing import Any, Dict, List, Optional
from .utils import hash_pass, hash_session, generate_client_hash
from .base_client import BaseClient, generate_client_id

TESTNET = False


class INNClient(BaseClient):
    def __init__(self, host_url: str, api_key: Optional[str] = None):
        super().__init__(host_url, api_key)

    def do_login(self, user: str, password: str, require_success: bool = True):
        login_body = {
            "user": user,
            "pass": hash_pass(password, user),
        }

        my_url = "/login"
        res_j = self._send_request(url=my_url, body=login_body)
        if not require_success:
            return res_j

        if "uuid" not in res_j:
            raise RuntimeError(f"Missing uuid in login response: {res_j}")

        self.email = res_j["email"]
        self.uuid = res_j["uuid"]
        self.username = res_j["username"]
        self.password = password
        self.pub = res_j["pub"]
        return res_j

    def passive_login(self, user: str, password: str):
        login_body = {
            "user": user,
            "pass": hash_pass(password, user),
        }

        my_url = "/login"
        res_j = self._send_request(url=my_url, body=login_body)
        if new_uuid := res_j.get("uuid"):
            self.uuid = new_uuid
        return res_j

    def do_logout(self):
        body = {"uuid": self.uuid} if self.uuid else {}
        my_url = "/auth/logout"
        return self._send_request(url=my_url, body=body)

    def validate_session(self, user: str, session: UUID):
        body = {"user": user, "sessionHash": hash_session(session)}
        my_url = "/auth/session/validate"
        return self._send_request(my_url, body)

    def resend_verification(self, other_fields: Optional[Dict] = None):
        resend_body = {"email": self.email}
        if other_fields:
            resend_body.update(other_fields)

        my_url = "/auth/email/resend"
        return self._send_request(my_url, resend_body)

    def verify_by_code(self, verify_code: str):
        if not verify_code:
            return False
        verify_url = f"{self.host_url}/verify/{verify_code}"
        res = requests.get(verify_url)
        return res.text

    def request_password_reset(self, other_fields: Optional[Dict] = None):
        body = {"username": self.username}
        if other_fields:
            body.update(other_fields)

        my_url = "/auth/password/forgot"
        return self._send_request(my_url, body)

    def request_username(self, other_fields: Optional[Dict] = None):
        body = {"email": self.email}
        if other_fields:
            body.update(other_fields)
        verify_url = "/auth/username/forgot"
        return self._send_request(verify_url, body)

    def change_password(self, old_pass: str, new_pass: str) -> Dict:
        user_pass = hash_pass(new_pass, self.username)
        email_pass = hash_pass(new_pass, self.email)
        body = {
            "uuid": self.uuid,
            "user": self.username,
            "oldPass": hash_pass(old_pass, self.username),
            "newPass": user_pass,
            "email": self.email,
            "newEmailHash": email_pass,
        }
        return self._send_request("/auth/password/change", body)

    def modify_settings(
        self, user="", email="", full_name=None, phone=None, tfa_enabled=None
    ):
        body = {
            "uuid": self.uuid,
            "user": user or self.username,
            "pass": hash_pass(self.password, self.username),
            "email": email or self.email,
        }

        if phone is not None:
            body["phone"] = phone
        if tfa_enabled is not None:
            body["tfaEnabled"] = tfa_enabled
        if full_name is not None:
            body["fullName"] = full_name

        return self._send_request("/core/settings/modify", body)

    def waitfor_status(self, client_id):
        i_max = 30
        i = 0
        while True:
            time.sleep(1)
            i = i + 1
            res = self.do_check_status([client_id])
            if res.get("clientTxs")[0].get("status") == "Rejected":
                return True
            if res.get("clientTxs")[0].get("status") == "Final":
                return True
            if i >= i_max:
                return False

    def waitfor_possession(self, nft_uri):
        i_max = 30
        i = 0
        while True:
            time.sleep(1)
            i = i + 1
            nfts = self.list_nfts({"nftUris": nft_uri})
            if len(nfts) > 0:
                return True
            if i >= i_max:
                return False

    def get_nft_reports(self, coin_ids):
        body = {"uuid": self.uuid, "coinIds": coin_ids, "perPage": 1000}

        my_url = "/core/nft/reports"
        return self._send_request(url=my_url, body=body)

    def do_check_status(self, client_ids: list):
        body = {"uuid": self.uuid, "clientIds": client_ids}

        my_url = "/core/transactions/status"
        return self._send_request(url=my_url, body=body)

    def get_incomplete_txs(self):
        body = {"uuid": self.uuid}

        my_url = "/core/transactions/incomplete"
        return self._send_request(url=my_url, body=body)

    def register(self, body: Dict, allow_login: bool = False):
        my_url = "/register"
        res_j = self._send_request(url=my_url, body=body)

        self.username = body["user"]

        if "uuid" not in res_j:
            return res_j

        self.email = res_j["email"]
        self.uuid = res_j["uuid"]
        self.pub = res_j["pub"]
        return res_j

    def list_nfts(self, body=None):
        inner_body = {"uuid": self.uuid, "perPage": 1000}
        if body:
            inner_body.update(body)
        my_url = "/core/nft/list"
        res_j = self._send_request(url=my_url, body=inner_body)
        if nfts := res_j.get("nfts"):
            return nfts
        return []

    def define_recipe(self, name: str, inputs: List, outputs: List):
        body = {"uuid": self.uuid, "name": name, "inputs": inputs, "outputs": outputs}
        my_url = "/recipe/define"
        return self._send_request(url=my_url, body=body)

    def list_recipes(self, owner_address: str):
        body = {"uuid": self.uuid, "owner": owner_address}
        my_url = "/recipe/list"
        return self._send_request(url=my_url, body=body)

    def use_recipe(self, recipe_uri, inputs):
        client_id = generate_client_id()
        for inp in inputs:
            inp["checksum"] = generate_client_hash(
                coin_id=inp.get("coinId"),
                client_secret=self.api_key,
                amount=inp.get("amount"),
                client_id=client_id,
            )
        body = {
            "uuid": self.uuid,
            "recipeUri": recipe_uri,
            "inputs": inputs,
            "clientId": client_id,
        }
        my_url = "/recipe/use"
        return self._send_request(url=my_url, body=body)

    def get_all_nfts(self, body=None):
        inner_body = {"uuid": self.uuid, "perPage": 1000}
        if body:
            inner_body.update(body)
        return self._send_request(url="/core/nft/all", body=inner_body)

    def get_nft_history(self, body=None):
        initial_body = {"uuid": self.uuid, "perPage": 1000}
        if body:
            initial_body.update(body)
        return self._send_request(url="/core/nft/history", body=initial_body)

    def get_nft_by_uri(self, nft_uri):
        body = {
            "uuid": self.uuid,
            "nftUris": [nft_uri],
        }

        my_url = "/core/nft/list"
        res_j = self._send_request(url=my_url, body=body)
        if not res_j.get("nfts"):
            return None
        return res_j.get("nfts")[0]

    def get_nft_balances(
        self,
        mint_ids: Optional[List[str]] = None,
        nft_names: Optional[List[str]] = None,
        version: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Dict[str, Any]]:
        body = {"uuid": self.uuid}
        if mint_ids is not None:
            body["mintIds"] = mint_ids
        if nft_names is not None:
            body["nftNames"] = nft_names
        if per_page:
            body["perPage"] = per_page
        if page:
            body["page"] = page
        my_url = (
            "/core/nft/balances" if version is None else f"/{version}/core/nft/balances"
        )

        return self._send_request(url=my_url, body=body)

    def send_nft(self, nft_uri, receiver_addr, optionals=None):
        body = {"uuid": self.uuid, "nftUri": nft_uri, "recipientAddr": receiver_addr}
        if optionals:
            body.update(optionals)
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )
        return self._send_request(url="/core/nft17/send", body=body)

    def check_balances(
        self,
        coins: List[int],
        block_height: int = -1,
        other_fields: Optional[Dict] = None,
    ):
        body = {"uuid": self.uuid, "coinIds": [str(coin) for coin in coins]}
        if other_fields:
            body.update(other_fields)
        if block_height >= 0:
            body["endBlock"] = block_height
        my_url = "/core/wallet/balances"
        return self._send_request(url=my_url, body=body)

    def get_wallet_assets(
        self, coins: Optional[List[int]] = None, asset_uris: Optional[List[str]] = None
    ):
        body = dict()
        if coins:
            body["coinIds"] = [str(coin) for coin in coins]
        if asset_uris:
            body["assetUris"] = asset_uris
        body["uuid"] = self.uuid
        my_url = "/core/wallet/assets"
        return self._send_request(url=my_url, body=body)

    def get_wallet_settings(self):
        body = {"uuid": self.uuid}
        my_url = "/core/wallet/settings"
        return self._send_request(url=my_url, body=body)

    def define_template(self, body: Dict):
        body["uuid"] = self.uuid
        my_url = "/core/template/define"
        return self._send_request(url=my_url, body=body)

    def describe_template(self, body: Dict):
        my_url = "/core/template/describe"
        return self._send_request(url=my_url, body=body)

    def list_template(self, body: Dict):
        body["uuid"] = self.uuid
        return self._send_request(url="/core/template/list", body=body)

    def get_asset_history(self, asset_uri: str):
        body = {"uuid": self.uuid, "assetUri": asset_uri}
        my_url = "/core/asset/history"
        return self._send_request(url=my_url, body=body)

    def do_asset_create(
        self,
        coin_id: int,
        amount: int,
        client_id: Optional[str] = None,
        properties: Optional[Dict] = None,
        comment: Optional[str] = None,
        sync: bool = True,
    ):
        body: Dict[str, Any] = {
            "uuid": self.uuid,
            "coinId": coin_id,
            "amount": amount,
        }
        if client_id:
            body["clientId"] = client_id
            checksum = generate_client_hash(
                coin_id, str(self.api_key), amount, client_id
            )
            body["checksum"] = f"{checksum}"
        else:
            if not TESTNET:
                client_id = generate_client_id()
                body["clientId"] = client_id
                checksum = generate_client_hash(
                    coin_id, str(self.api_key), amount, client_id
                )
                body["checksum"] = f"{checksum}"

        if properties:
            body["properties"] = properties
        if comment:
            body["comment"] = comment
        # if not sync:
        #    body["noBlock"] = True
        res = self._send_request(url="/core/asset/create", body=body)
        if sync and not res.get("code"):
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Create tx timed out"
        return res

    def register_callback(
        self,
        callback_url: str,
        condition: str,
        condition_value: str,
        method: str,
        auth_token: str,
        num_calls: Optional[int] = None,
    ):
        body = {
            "uuid": self.uuid,
            "callbackUrl": callback_url,
            "condition": condition,
            "conditionValue": str(condition_value),
            "numCalls": num_calls,
            "method": method,
            "authToken": auth_token,
        }

        res = self._send_request(url="/callback/register", body=body)
        return res

    def delete_callback(
        self,
        callback_id: str,
    ):
        body = {
            "uuid": self.uuid,
            "callbackId": callback_id,
        }

        res = self._send_request(url="/callback/delete", body=body)
        return res

    def list_callbacks(
        self,
        callback_id: Optional[str] = None,
    ):
        body = {
            "uuid": self.uuid,
            "callbackId": callback_id,
        }

        res = self._send_request(url="/callback/list", body=body)
        return res

    def delete_asset(
        self,
        coin_id: int,
        amount: int,
        client_id: Optional[str] = None,
        asset_uri: Optional[str] = None,
        comment: Optional[str] = None,
        other_fields: Optional[Dict] = None,
        sync: bool = True,
    ):
        body = {"uuid": self.uuid, "coinId": str(coin_id), "amount": str(amount)}
        if client_id:
            body["clientId"] = client_id
            checksum = generate_client_hash(
                coin_id, str(self.api_key), amount, client_id
            )
            body["checksum"] = f"{checksum}"
        else:
            if not TESTNET:
                client_id = generate_client_id()
                body["clientId"] = client_id
                checksum = generate_client_hash(
                    coin_id, str(self.api_key), amount, client_id
                )
                body["checksum"] = f"{checksum}"
        if asset_uri:
            body["assetUri"] = asset_uri
        if comment:
            body["comment"] = comment
        if other_fields:
            body.update(other_fields)

        res = self._send_request(url="/core/asset/delete", body=body)
        if sync:
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Delete tx timed out"
        return res

    def modify_asset(
        self,
        coin_id: int,
        asset_uri: str,
        properties: Dict,
        client_id: str,
        comment: Optional[str] = None,
        checksum: Optional[str] = None,
        devv_protect: Optional[bool] = None,
        protect_time: Optional[int] = None,
        sync: bool = True,
    ):
        body = {
            "uuid": self.uuid,
            "coinId": coin_id,
            "assetUri": asset_uri,
            "properties": properties,
            "clientId": client_id,
        }
        if comment is not None:
            body["comment"] = comment
        if checksum is None:
            checksum = generate_client_hash(coin_id, str(self.api_key), 1, client_id)
        body["checksum"] = checksum
        if devv_protect is not None:
            body["devvProtect"] = devv_protect
        if protect_time is not None:
            body["protectTime"] = protect_time

        res = self._send_request(url="/core/asset/modify", body=body)
        if sync:
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Modify tx timed out"
        return res

    def mint_nft(self, body: dict):
        body["uuid"] = self.uuid
        if not body.get("clientId"):
            client_id = generate_client_id()
            body["clientId"] = client_id
        if not body.get("checksum") and not body.get("checkSum"):
            body["checksum"] = generate_client_hash(
                17,
                client_secret=self.api_key,
                amount=body.get("amount", 1),
                client_id=client_id,
            )
        my_url = "/core/nft/mint"

        return self._send_request(url=my_url, body=body)

    def sell_nft(self, nft_uri: str, client_id: str, body: dict = None):
        checksum = generate_client_hash(
            coin_id=17, client_secret=self.api_key, amount=1, client_id=client_id
        )
        body["clientId"] = client_id
        body["checksum"] = checksum
        body["nftUri"] = nft_uri
        if self.uuid:
            body["uuid"] = self.uuid

        my_url = "/core/nft/sell"
        return self._send_request(url=my_url, body=body)

    def retract_nft(self, nft_uri: str, client_id: str):
        checksum = generate_client_hash(
            coin_id=17, client_secret=self.api_key, amount=1, client_id=client_id
        )
        body = {
            "uuid": self.uuid,
            "nftUri": nft_uri,
            "clientId": client_id,
            "checksum": checksum,
        }

        my_url = "/core/nft/retract"
        return self._send_request(url=my_url, body=body)

    def request_nft_refund(
        self,
        description: str,
        nft_uri: str,
        client_id: Optional[str] = None,
        other_fields: Optional[Dict] = None,
    ):
        if not client_id:
            client_id = str(uuid4())
        inner_body = {
            "uuid": self.uuid,
            "description": description,
            "nftUri": nft_uri,
            "clientId": client_id,
            "checksum": generate_client_hash(17, self.api_key, 1, client_id),
        }
        if other_fields:
            inner_body.update(other_fields)

        my_url = "/core/asset/return"
        return self._send_request(url=my_url, body=inner_body)

    def request_asset_refund(
        self,
        description: str,
        asset_uri: str,
        coin_id: int,
        client_id: Optional[str] = None,
        other_fields: Optional[Dict] = None,
    ):
        if not client_id:
            client_id = str(uuid4())
        inner_body = {
            "uuid": self.uuid,
            "description": description,
            "assetUri": asset_uri,
            "clientId": client_id,
            "coinId": coin_id,
            "checksum": generate_client_hash(coin_id, self.api_key, 1, client_id),
        }
        if other_fields:
            inner_body.update(other_fields)

        my_url = "/core/asset/return"
        return self._send_request(url=my_url, body=inner_body)

    def request_token_refund(
        self,
        description: str,
        amount: int,
        coin_id: int,
        client_id: Optional[str] = None,
        other_fields: Optional[Dict] = None,
    ):
        if not client_id:
            client_id = str(uuid4())
        inner_body = {
            "uuid": self.uuid,
            "description": description,
            "amount": amount,
            "coinId": coin_id,
            "clientId": client_id,
            "checksum": generate_client_hash(coin_id, self.api_key, amount, client_id),
        }
        if other_fields:
            inner_body.update(other_fields)

        my_url = "/core/asset/return"
        return self._send_request(url=my_url, body=inner_body)

    def checkout_nft(self, buyer_address: str, nft_uri: str):
        body = {
            "uuid": self.uuid,
            "nftUri": nft_uri,
            "buyerAddress": buyer_address,
        }

        my_url = "/core/nft/checkout"
        return self._send_request(my_url, body)

    def fulfill_nft(
        self, buyer_address: str, nft_uri: str, checksum: Optional[str] = None
    ):
        body = {
            "uuid": self.uuid,
            "nftUri": nft_uri,
            "buyerAddress": buyer_address,
            "checksum": checksum,
        }
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )

        my_url = "/core/nft/fulfill"
        return self._send_request(my_url, body)

    def unbundle_nft(self, nft_uri: str):
        body = {"uuid": self.uuid, "nftUri": nft_uri}

        my_url = "/core/nft/unbundle"
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )
        return self._send_request(my_url, body)

    def escrow_unbundle_nft(self, nft_uri: str):
        body = {"uuid": self.uuid, "nftUri": nft_uri}
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )
        my_url = "/core/escrow/unbundle"
        return self._send_request(my_url, body)

    def upload_content(
        self,
        content_name: str,
        content_type: str,
        field_schema: Dict,
        content_raw: str,
        other_fields: Optional[Dict] = None,
    ):
        body = {
            "uuid": self.uuid,
            "content": {
                "raw": content_raw,
                "contentType": content_type,
                "fieldSchema": field_schema,
            },
            "name": content_name,
        }
        if other_fields:
            body.update(other_fields)

        my_url = "/core/content/upload"
        res_j = self._send_request(my_url, body)
        if content_ref := res_j.get("contentRef"):
            return content_ref
        return res_j

    def download_content(self, content_uri: str):
        body = {"contentRef": content_uri}

        my_url = "/core/content/download"
        res_j = self._send_request(my_url, body)

        if content := res_j.get("content"):
            return content
        return None

    def get_asset_by_uri(self, asset_uri: str):
        body = {"uuid": self.uuid, "assetUris": [asset_uri]}

        my_url = "/core/wallet/assets"
        res_j = self._send_request(my_url, body)
        if assets := res_j.get("assets"):
            return assets[0]
        return None

    def get_balance(self, coin_id: int):
        body = {"uuid": self.uuid, "coinIds": [str(coin_id)]}

        my_url = "/core/wallet/balances"
        res_j = self._send_request(my_url, body)
        if (balances := res_j.get("balances")) and (
            balance := balances[0].get("balance")
        ):
            return balance
        return 0

    def search_username(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/search/username"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def get_support_verification(
        self, user: Optional[str] = None, email: Optional[str] = None
    ):
        body = {"uuid": self.uuid}
        if user:
            body["user"] = user
        if email:
            body["email"] = email
        my_url = "/tools/test/verification"
        return self._send_request(url=my_url, body=body)

    def get_wallet_addr(self):
        body = {
            "uuid": self.uuid,
            "name": self.username,
        }

        res_j = self.search_username(body)

        wallet_addr = res_j.get("wallets")
        if wallet_addr:
            return wallet_addr[0].get("addr")

        return wallet_addr

    def get_shard_info(self):
        """
        Send a request to retrieve information about the shard from the specified endpoint.
        :returns: A dictionary representing the JSON response received from the shard info endpoint.
        """
        my_url = "/core/shard/info"
        return self._send_get_request(url=my_url)

    def get_shard_configs(self):
        return self._send_get_request(url="/core/settings/configs")

    def get_settings_home(self):
        """
        Retrieve home settings from the user's shard.
        :return: A dictionary containing home settings retrieved from the shard.
        """
        body = {
            "uuid": self.uuid,
        }
        my_url = "/core/settings/home"
        return self._send_request(url=my_url, body=body)

    def get_transaction_info(self, body):
        """
        Send a request to retrieve information about the transaction from the specified endpoint.
        :param body: A dictionary containing the request body to be sent in JSON format.
        :returns: A dictionary representing the JSON response received from the transaction info endpoint.
        """
        my_url = "/core/transaction/info"
        return self._send_post_request(url=my_url, body=body)

    def get_block_info(self, body):
        my_url = "/core/block/info"
        return self._send_request(url=my_url, body=body)

    def get_block_chart(self, body):
        my_url = "/core/block/chart"
        return self._send_post_request(url=my_url, body=body)

    def create_chest_litpet(self):
        body = {
            "uuid": self.uuid,
        }
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )

        my_url = "/litcraft/chest/litpet"
        return self._send_request(url=my_url, body=body)

    def make_litpet(self, mother_uri, father_uri, receiver_address, heptal_count=1000):
        body = {
            "uuid": self.uuid,
            "targetAddr": receiver_address,
            "motherUri": mother_uri,
            "fatherUri": father_uri,
            "heptalCount": heptal_count,
            "magicLevel": random.randint(1, 7),
        }
        if not TESTNET:
            client_id = generate_client_id()
            body.update(
                {
                    "clientId": client_id,
                    "checksum": generate_client_hash(
                        17, client_secret=self.api_key, amount=1, client_id=client_id
                    ),
                }
            )

        my_url = "/litcraft/litpet/create"
        return self._send_request(url=my_url, body=body)

    def make_server_litpet(
        self,
        mother_species: str,
        father_species: str,
        target_addr: str,
        magic_level: Optional[int] = None,
    ):
        body = {
            "uuid": self.uuid,
            "motherSpecies": mother_species,
            "fatherSpecies": father_species,
            "magicLevel": magic_level or random.randint(1, 7),
            "targetAddr": target_addr,
        }
        my_url = "/litcraft/litpet/servercreate"
        return self._send_request(url=my_url, body=body)

    def view_litpet(self, litpet_uri):
        body = {"uuid": self.uuid, "litpetUri": litpet_uri}

        my_url = "/litcraft/litpet/view"
        return self._send_request(url=my_url, body=body)

    def player_assets(self, pub: str):
        """
        Fetches the assets associated with a player's public key.
        :param pub: The public key of the player.
        :returns: A dictionary containing the player's assets information.
        """
        body = {"uuid": self.uuid, "pub": pub}
        my_url = "/litcraft/player/assets"
        return self._send_request(url=my_url, body=body)

    def player_balances(self, pub: str):
        """
        Retrieves the balances of a player's assets based on their public key.
        :param pub: The public key of the player.
        :returns: A dictionary containing the player's asset balances.
        """
        body = {"uuid": self.uuid, "pub": pub}
        my_url = "/litcraft/player/balances"
        return self._send_request(url=my_url, body=body)

    def send_transaction(
        self,
        coin_id: int,
        amount: int,
        receiver_address,
        asset_uri: Optional[str] = None,
        comment: Optional[str] = None,
        client_id: Optional[str] = None,
        sync: bool = True,
    ):
        body = {
            "uuid": self.uuid,
            "wallet": self.get_wallet_addr(),
            "to": receiver_address,
            "coinId": str(coin_id),
            "amount": amount,
            "hex": "",
            "sig": "",
            "assetUri": asset_uri,
        }
        if asset_uri:
            body["assetUri"] = asset_uri
        if client_id:
            body["clientId"] = client_id
            body["checksum"] = generate_client_hash(
                coin_id, client_secret=self.api_key, amount=amount, client_id=client_id
            )
        if not TESTNET and not client_id:
            client_id = generate_client_id()
            body["clientId"] = client_id
            body["checksum"] = generate_client_hash(
                coin_id, client_secret=self.api_key, amount=amount, client_id=client_id
            )
        if comment:
            body["comment"] = comment

        res = self._send_request(url="/core/transactions/send", body=body)
        if sync:
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Send tx timed out"
        return res

    def core_account_settings(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/account/settings"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def core_settings_modify(self, body: Optional[Dict] = None):
        init_body = {
            "uuid": self.uuid,
            "user": self.username,
            "pass": hash_pass(self.password, self.username),
        }
        if body:
            init_body.update(body)

        my_url = "/core/settings/modify"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def core_account_assets(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/account/assets"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def core_account_balances(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/account/balances"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def core_account_transactions(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/account/transactions"
        res_j = self._send_request(url=my_url, body=init_body)

        return res_j

    def core_escrow_bundle(self, body: Dict, sync: bool = True):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        if not TESTNET and not init_body.get("clientId", None):
            client_id = generate_client_id()
            init_body["clientId"] = client_id
            init_body["checksum"] = generate_client_hash(
                coin_id=init_body.get("bundleCoinId", 17),
                client_secret=self.api_key,
                amount=init_body.get("bundleAmount", 1),
                client_id=client_id,
            )

        res = self._send_request(url="/core/escrow/bundle", body=init_body)
        if sync and "clientId" in res:
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Escrow bundle timed out"

        return res

    def core_escrow_unbundle(self, body: Dict, sync: bool = True):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        if not TESTNET and not init_body.get("clientId", None):
            client_id = generate_client_id()
            init_body["clientId"] = client_id
            init_body["checksum"] = generate_client_hash(
                init_body.get("coindId", 17),
                client_secret=self.api_key,
                amount=init_body.get("coindId", 1),
                client_id=client_id,
            )

        res = self._send_request(url="/core/escrow/unbundle", body=init_body)
        if sync and "clientId" in res:
            wait_res = self.waitfor_status(client_id=res.get("clientId"))
            assert wait_res, "[x] Escrow unbundle timed out"

        return res

    def core_transactions_final(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/core/transactions/final"
        res_j = self._send_request(url=my_url, body=init_body)
        return res_j

    def identity_presale_individual(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/identity/presale/individual"
        res_j = self._send_request(url=my_url, body=init_body)
        return res_j

    def identity_kyc_view(self, body: Dict):
        init_body = {"uuid": self.uuid}
        init_body.update(body)

        my_url = "/identity/kyc/view"
        res_j = self._send_request(url=my_url, body=init_body)
        return res_j

    def core_list_roles(self, usernames: Optional[List[str]] = None):
        """
        List the roles of a user.
        List the roles of a group of users (Admin only).
        :param usernames: A list containing the usernames of the users for which to fetch the roles as strings.
        :returns: A dictionary that will contain the usernames as keys and the roles as a list of strings as values.
        """
        body: Dict[str, Any] = {"uuid": self.uuid}
        if usernames:
            body.update({"usernames": usernames})
        my_url = "/core/roles/list"
        res_j = self._send_request(url=my_url, body=body)
        return res_j

    def core_grant_role_permissions(self, body: Dict):
        """
        Grant role permissions to the current user or entity.
        :param body: A dictionary containing the role assignment information. This should include details such as
        the target user or entity and the specific roles to be assigned.
        :returns: A dictionary that will contain information about the success or failure of the role assignment.
        """
        init_body = {"uuid": self.uuid}
        init_body.update(body)
        my_url = "/core/roles/assign"
        res_j = self._send_request(url=my_url, body=init_body)
        return res_j

    def core_revoke_role_permissions(self, body: Dict):
        """
        Revoke role permissions from the current user or entity.
        :param body: A dictionary containing the role revocation information. This should include details such as
        the target user or entity and the specific roles to be revoked.
        :returns: A dictionary that will contain information about the success or failure of the role revocation.
        """
        init_body = {"uuid": self.uuid}
        init_body.update(body)
        my_url = "/core/roles/revoke"
        res_j = self._send_request(url=my_url, body=init_body)
        return res_j

    def delete_account(self, admin_session: str = None, admin_access_token: str = None):
        body = {
            "user": self.username,
        }

        if self.access_token:
            body["targetAccessToken"] = self.access_token
            self.access_token = None
        elif self.uuid:
            body["sessionHash"] = hash_session(self.uuid)
        else:
            raise ValueError("Client not logged in. Cannot delete account.")

        if admin_access_token:
            self.access_token = admin_access_token
        elif admin_session:
            body["uuid"] = admin_session

        my_url = "/auth/account/delete"
        res = self._send_request(url=my_url, body=body)
        self.access_token = body.get("targetAccessToken")

        return res

    def get_oauth_settings(self):
        body = dict()
        if self.uuid:
            body["uuid"] = self.uuid
        my_url = "/auth/wallet/settings"
        return self._send_request(url=my_url, body=body)

    def modify_oauth_settings(
        self, user="", email="", full_name=None, phone=None, tfa_enabled=None
    ):
        body = dict()
        body["username"] = user or self.username

        if email:
            body["email"] = email
        if self.uuid and not self.access_token:
            body["uuid"] = self.uuid
        if phone is not None:
            body["phone"] = phone
        if tfa_enabled is not None:
            body["tfaEnabled"] = tfa_enabled
        if full_name is not None:
            body["fullName"] = full_name

        return self._send_request("/auth/settings/modify", body)

    def register_oauth_callback(self, callback_uri: str):
        body = {
            "callbackUri": callback_uri,
        }

        if self.uuid:
            body["uuid"] = self.uuid

        my_url = "/auth/callback/register"
        return self._send_request(url=my_url, body=body)

    def remove_oauth_callback(self, callback_uri: str):
        body = {
            "callbackUri": callback_uri,
        }

        if self.uuid:
            body["uuid"] = self.uuid

        my_url = "/auth/callback/remove"
        return self._send_request(url=my_url, body=body)

    def do_oauth_login(
        self, username: str, password: str, require_success: bool = True
    ):
        login_body = {
            "username": username,
            "password": password,
        }

        my_url = "/auth/login"
        res_j = self._send_request(url=my_url, body=login_body)
        if not require_success:
            return res_j

        if "authorizationCode" not in res_j:
            if "accessToken" not in res_j:
                raise RuntimeError(f"Missing accessToken in login response: {res_j}")
            if "refreshToken" not in res_j:
                raise RuntimeError(f"Missing refreshToken in login response: {res_j}")

            self.access_token = res_j["accessToken"]
            self.refresh_token = res_j["refreshToken"]
            self.id_token = res_j["idToken"]
        self.email = res_j["email"]
        self.username = username
        self.password = password
        self.pub = res_j["pub"]
        return res_j

    def do_oauth_code_grant(
        self, username: str, password: str, require_success: bool = True
    ):
        login_body = {
            "username": username,
            "password": password,
            "returnAuthorizationCode": True,
        }

        my_url = "/auth/login"
        res_j = self._send_request(url=my_url, body=login_body)

        if not require_success:
            return res_j

        if "authorizationCode" not in res_j:
            raise RuntimeError(f"Missing authorizationCode in login response: {res_j}")

        if "accessToken" in res_j:
            raise RuntimeError(f"Unexpected accessToken in login response: {res_j}")

        self.email = res_j["email"]
        self.username = username
        self.password = password
        self.pub = res_j["pub"]
        return res_j

    def do_oauth_code_exchange(self, code: str, require_success: bool = True):
        my_url = f"/auth/login?code={code}"
        res_j = self._send_request(url=my_url, body={})
        if not require_success:
            return res_j
        if not res_j.get("accessToken"):
            raise RuntimeError(f"Missing accessToken in login response: {res_j}")
        self.access_token = res_j["accessToken"]
        self.refresh_token = res_j["refreshToken"]
        self.id_token = res_j["idToken"]
        return res_j

    def request_oauth_window(self, callback_uri: str = None, apikey: str = None):
        my_url = "/auth/oauth?"
        if apikey:
            my_url += f"apikey={apikey}"
        if self.api_key and not apikey:
            my_url += f"apikey={self.api_key}"
        if callback_uri:
            my_url += "&" if (apikey or self.api_key) else ""
            my_url += f"callbackUri={quote_plus(callback_uri)}"
        return requests.get(f"{self.host_url}{my_url}")

    def change_oauth_password(self, old_pass: str, new_pass: str) -> dict:
        body = {
            "user": self.username,
            "oldPass": old_pass,
            "newPass": new_pass,
            "email": self.email,
        }
        return self._send_request("/auth/password/update", body)

    def reset_password(
        self, reset_code: str, new_pass: str, other_fields: Optional[dict] = None
    ):
        body = {
            "username": self.username,
            "email": self.email,
            "resetCode": reset_code,
            "newPassword": new_pass,
        }
        if other_fields:
            body.update(other_fields)
        my_url = "/auth/password/reset"
        return self._send_request(url=my_url, body=body)

    def do_oauth_register(
        self,
        username: str,
        password: str,
        full_name: str,
        email: str,
        phone: str = None,
        allow_login: bool = True,
    ) -> dict:
        register_body = {
            "username": username,
            "password": password,
            "fullName": full_name,
            "email": email,
        }
        if phone:
            register_body["phone"] = phone

        my_url = "/auth/register"
        res_j = self._send_request(url=my_url, body=register_body)

        if res_j.get("accessToken"):
            self.access_token = res_j["accessToken"]
            self.refresh_token = res_j["refreshToken"]
            self.id_token = res_j["idToken"]
            self.username = username
            self.password = password
            self.pub = res_j["pub"]
        return res_j

    def do_oauth_refresh(self) -> dict:
        if not self.refresh_token:
            raise RuntimeError("Missing refresh token")

        refresh_body = {
            "refreshToken": self.refresh_token,
            "accessToken": self.access_token,
        }

        my_url = "/auth/refresh"
        res_j = self._send_request(url=my_url, body=refresh_body)

        if res_j.get("accessToken"):
            self.access_token = res_j["accessToken"]
            self.id_token = res_j["idToken"]

        return res_j

    def verify_oauth_user(self, username: str):
        body = {
            "username": username,
        }

        if self.uuid:
            body["uuid"] = self.uuid

        my_url = "/auth/tools/verification"
        return self._send_request(url=my_url, body=body)

    def oauth_mfa_initiate(self) -> dict:
        body = {}
        my_url = "/auth/mfa/initiate"
        return self._send_request(url=my_url, body=body)

    def oauth_mfa_enable(self, totp_code: str) -> dict:
        body = {
            "totpCode": totp_code,
        }
        my_url = "/auth/mfa/enable"
        return self._send_request(url=my_url, body=body)

    def oauth_mfa_disable(self) -> dict:
        if not self.password:
            raise ValueError("Client password must be initialized to disable MFA.")
        body = {
            "password": self.password,
        }
        my_url = "/auth/mfa/disable"
        return self._send_request(url=my_url, body=body)

    def oauth_mfa_respond(self, totp_code: str, authorization_code: str) -> dict:
        body = {
            "totpCode": totp_code,
            "authorizationCode": authorization_code,
            "username": self.username,
        }
        my_url = "/auth/mfa/respond"
        return self._send_request(url=my_url, body=body)


class INNTestClient(INNClient):
    def __init__(self, host_url: str, api_key: Optional[str] = None):
        super().__init__(host_url, api_key)

    @staticmethod
    def register_users(
        host_url: str, n: int, offset: int, apikey: str = None
    ) -> list[dict]:
        """Register n users with the name test_{i} starting from i = offset."""
        users = []
        for i in range(n):
            user = {}
            acct_num = i + offset
            acct_pass = f"Test_user_{acct_num}!"
            acct_name = f"test_{acct_num}"
            phone = "+13014000000"
            phone = phone[: -len(str(acct_num))] + str(acct_num)
            body = {
                "addr": "",
                "user": acct_name,
                "pass": hash_pass(acct_pass, acct_name),
                "fullName": f"Test {acct_num}",
                "email": f"test+{acct_num}@example.com",
                "phone": phone,
                "apikey": apikey,
            }
            myurl = f"{host_url}/register"
            res = requests.post(
                myurl,
                json=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
                verify=True,
            ).json()
            user["user"] = acct_name
            user["pass"] = acct_pass
            user["pub"] = res.get("pub")
            user["acctNum"] = acct_num
            user["username"] = acct_name
            user["email"] = f"test+{acct_num}@example.com"
            user["phone"] = phone
            users.append(user)

        return users

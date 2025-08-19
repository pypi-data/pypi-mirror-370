import requests
import logging
from hashlib import sha256
from typing import Dict, List, Optional
from .base_client import BaseClient


class DFEClient(BaseClient):
    """ """

    def __init__(self, host_url: str, api_key: Optional[str] = None):
        super().__init__(host_url, api_key)

    def request_register(
        self, user, password, fullname, email, apikey, phone=None, addr=""
    ):
        body = {
            "user": user,
            "passwd": password,
            "fullname": fullname,
            "email": email,
            "apiKey": apikey,
            "phone": phone,
            "addr": addr,
        }

        my_url = "/lc/v1/register"
        return self._send_post_request(my_url, body)

    def request_login(self, other_fields: dict = None):
        # TODO Refactor hardcoded values
        body = {
            "clientInfo": "doesnt matter",
            "lcServerVersion": "9.9.9",
            "otp": "",
        }
        if other_fields:
            body.update(other_fields)

        my_url = "/lc/v1/user/login_pt"
        res = self._send_post_request(my_url, body)
        self.username = res.get("username")
        self.uuid = res.get("uuid")
        self.pub = res.get("pub")

        return res

    def request_bc2db(self, other_fields: dict = None):
        body = {}
        if other_fields:
            body.update(other_fields)

        my_url = "/dfe/v1/inventory/bc2db"
        return self._send_post_request(my_url, body)

    def create_litpet(
        self, username, hashed_uuid, target_addr, magic_type, food1_type, food2_type
    ):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
            "client_addr": target_addr,
            "pet1_uri": "",
            "pet2_uri": "",
            "magic_type": magic_type,
            "food1_type": food1_type,
            "food2_type": food2_type,
        }

        my_url = "/lc/v1/material/create_litpet"
        return self._send_post_request(my_url, body)

    def open_chest(self, position: str, category: str):
        body = {
            "username": self.username,
            "hashed_uuid": self.uuid,
            "asset_name": "LitPet Chest",
            "category": category,
            "position": position,
            "client_addr": self.pub,
        }

        my_url = "/lc/v1/open_chest"
        return self._send_post_request(my_url, body)

    def request_set_inventory(self, other_fields: dict = None):
        body = {
            "username": self.username,
            "hashed_uuid": self.uuid,
        }
        if other_fields:
            body.update(other_fields)

        my_url = "/dfe/v1/inventory/set_inventory"
        return self._send_post_request(my_url, body)

    def request_get_inventory(self, other_fields: dict = None):
        body = {}
        if other_fields:
            body.update(other_fields)

        my_url = "/dfe/v1/inventory/get_inventory"
        return self._send_post_request(my_url, body)

    def request_game_state(self, other_fields: dict = None):
        body = {}
        if other_fields:
            body.update(other_fields)

        my_url = "/lc/v1/game_state/get_game_state"
        return self._send_post_request(my_url, body)

    def request_subscription(self, other_fields: dict = None):
        body = {}
        if other_fields:
            body.update(other_fields)

        my_url = "/lc/v1/subscription"
        return self._send_post_request(my_url, body)

    def request_send_asset(self, other_fields: dict = None):
        body = {}
        if other_fields:
            body.update(other_fields)

        my_url = "/lc/v1/material/send_asset"
        return self._send_post_request(my_url, body)

    def request_callback(self, other_fields: dict = None, xfers: list = []):
        # TODO Refactor hardcoded values
        body = {
            "tx": {
                "op": "CREATE",
                "payload": "0004<505e3526-36c4-43ed-b0cd-28fc9a31a6cb<<<",
                "sig": (
                    "693064023078e035f0f31834fd3342623497ddf80232ec\
                6575c273a9acb9410cec1fd00c5f9c006c4a0fa8ab06a146a61ba01b\
                4a0702303ab40db4a89a40dbf3478045895a48cca5035d8956d8bd91d\
                f9da3f763ac437b093ef9ecd0563f6402a0de28ef6c6d94000000"
                ),
                "flags": 0,
                "timestamp": 0,
                "xfers": xfers,
            }
        }
        body["authToken"] = sha256(
            ("00000000-1111-1111-1111-111111111111" + body["tx"]["sig"]).encode()
        ).hexdigest()
        if other_fields:
            body.update(other_fields)

        my_url = "/dfe/v1/tx_notifications"
        return self._send_post_request(my_url, body)


class LLClient(BaseClient):
    def __init__(self, host_url):
        super().__init__(host_url)

    @staticmethod
    def create_dummy_tasks(host_url: str, n: int, offset: int) -> List[Dict]:
        """Create n tasks with the name test_task_{i} starting from i = offset."""
        tasks = []
        for i in range(n):
            task = {}
            task_num = i + offset
            task_name = f"test_task_{task_num}"
            body = {
                "name": task_name,
                "description": f"Task #{task_num}",
                "intro": "INTRO",
                "objectives": "OBJECTIVES",
                "progress": "IN PROGRESS",
                "success": "SUCCESS",
                "xp": 100,
            }
            my_url = "{}/ll/v1/admin/tasks/create".format(host_url)
            logging.info(f"create task url: {my_url} : body: {body}")
            res = requests.post(
                my_url,
                json=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
                verify=True,
            )
            logging.info(f"res: {res}")
            logging.info(f"res: {res.json()}")
            task["name"] = body["name"]
            tasks.append(task)

        return tasks

    def create_tasks(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/tasks/create"
        return self._send_post_request(url, body)

    def get_tasks(self):
        body = {}

        my_url = "{}/ll/v1/admin/tasks/get".format(self.host_url)
        logging.info(f"get tasks url: {my_url} : body: {body}")

        res = requests.post(
            my_url,
            json=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=True,
        )
        logging.info(f"res: {res}")
        logging.info(f"res: {res.json()}")
        return res

    def create_user_levels(
        self, username: str, hashed_uuid: str, other_fields: dict = None
    ):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/levels/create"
        return self._send_post_request(url, body)

    def get_user_levels(
        self, username: str, hashed_uuid: str, other_fields: dict = None
    ):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/levels/get"
        return self._send_post_request(url, body)

    def create_npcs(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/npcs/create"
        return self._send_post_request(url, body)

    def get_npcs(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/npcs/get"
        return self._send_post_request(url, body)

    def create_badges(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/badges/create"
        return self._send_post_request(url, body)

    def get_badges(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/badges/get"
        return self._send_post_request(url, body)

    def delete_badge(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/badges/delete"
        return self._send_post_request(url, body)

    def update_badge(self, username: str, hashed_uuid: str, other_fields: dict = None):
        body = {
            "username": username,
            "hashed_uuid": hashed_uuid,
        }
        if other_fields:
            body.update(other_fields)
        url = "/ll/v1/admin/badges/update"
        return self._send_post_request(url, body)

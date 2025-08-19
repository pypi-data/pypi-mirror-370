from base64 import b64encode
from hashlib import sha256
from uuid import UUID


def generate_client_hash(
    coin_id: int, client_secret: str, amount: int, client_id: str
) -> str:
    combined = str(coin_id) + str(client_secret) + str(amount) + str(client_id)
    return sha256(combined.encode("utf-8")).hexdigest()


def hash_pass(password: str, user: str):
    return sha256(f"{password}{user.lower()}".encode()).hexdigest()


def hash_session(session: UUID):
    return b64encode(bytes.fromhex(sha256(session.encode("utf-8")).hexdigest())).decode(
        "utf-8"
    )

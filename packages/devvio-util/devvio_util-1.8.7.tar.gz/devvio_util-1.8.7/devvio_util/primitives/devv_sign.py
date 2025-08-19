from devvio_util.primitives.signature import Signature
from devvio_util.primitives.address import Address
from devvio_util.primitives.devv_constants import (
    kWALLET_ADDR_SIZE,
    kNODE_ADDR_SIZE,
    kNODE_SIG_SIZE,
    kWALLET_SIG_SIZE,
    kPEM_PREFIX,
    kPEM_SUFFIX,
    kPEM_PREFIX_SIZE,
    kPEM_SUFFIX_SIZE,
)
from devvio_util.primitives.utils import set_uint8

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import serialization as sz
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import pkg_resources

kWALLET_CURVE = ec.SECP256K1()
kNODE_CURVE = ec.SECP384R1()


def crypto_sanity_check(
    pkey: str = None, pub: str or Address = None, aes_pass: str = None
) -> tuple:
    """
    Tests the cryptographic methods in this devv_sign module. Can be used to validate a given keypair and aes key,
    otherwise will generate a test key

    :param pkey: str of private key, without PEM prefix/suffix or newlines
    :type pkey: str
    :param pub: public key as a hex string or devvio-util Address object
    :type pub: str
    :param aes_pass: aes key to decrypt/encrypt the pkey with
    :type aes_pass: str
    :return: a tuple of strings displaying the distribution of the cryptography package in use by this module,
    alongside the OpenSSL version employed by said cryptography package
    :rtype: tuple
    """
    if not aes_pass:
        aes_pass = "password"
    if not pkey:
        ec_key = EcSigner(aes_pass=aes_pass)
        pub = ec_key.get_signer_addr()
        pkey = ec_key.get_pkey()
    msg = b"Testing"
    sign_binary(pkey, pub, msg, aes_pass)
    crypto_version = str(pkg_resources.get_distribution("cryptography"))
    openssl_version = backend.openssl_version_text()
    return openssl_version, crypto_version


def format_pkey(pkey: str) -> bytes:
    """
    Formats a plain private key to be loaded by EcSigner
    :param pkey: private key string with no newlines or PEM-prefixes/suffixes
    :type pkey: str
    :return: binary for the PEM-formatted key (with no newlines)
    :rtype: bytes
    """
    return bytes(kPEM_PREFIX + pkey + kPEM_SUFFIX, "utf-8")


def sign_binary(pkey: str, pub: str or Address, msg: bytes, aes_pass: str) -> Signature:
    """Signs the given msg binary using the given keypair and aes key, and validates the signature

    :param pkey: str of private key, without PEM prefix/suffix or newlines
    :type pkey: str
    :param pub: public key as a hex string or devvio-util Address object
    :type pub: str
    :param msg: contains the hashed binary to be signed
    :type msg: bytes
    :param aes_pass: aes key to decrypt/encrypt the pkey with; this is required
    :type aes_pass: str
    :return: a new signature for the given bytes object
    :rtype: Signature
    """
    try:
        pkey_bin = format_pkey(pkey)
        signer = EcSigner(pkey=pkey_bin, pub=pub, aes_pass=aes_pass)

        sig = signer.sign(msg)
        sig_size = len(sig)

        if sig_size < 80:
            pad_len = kWALLET_SIG_SIZE
        else:
            pad_len = kNODE_SIG_SIZE

        if sig_size < pad_len:
            padding = b""
            for i in range(pad_len - sig_size):
                padding += set_uint8(0)
            sig += padding
        elif sig_size > pad_len:
            sig = sig[:pad_len]

        return Signature(sig)
    except Exception as e:
        raise RuntimeError(f"Signature procedure failed ({e})")


class EcSigner:
    """Can be used to parse PEM files, generate keypairs, create signatures, and verify signatures."""

    def __init__(
        self,
        pkey: bytes = None,
        pub: str or Address = None,
        aes_pass: str = None,
        curve: ec.EllipticCurve = None,
    ):
        """Initialize a signer from a given keypair or a given curve.

        :param pkey: bytes of private key in PEM format
        :type pkey: bytes
        :param pub: public key as a hex string or devvio-util Address object
        :type pub: str
        :param aes_pass: aes key to decrypt/encrypt the PEM file with; this is required
        :type aes_pass: str
        :param curve: elliptic curve to use in generating/loading the key;
        defaults to devv_sign.kWALLET_CURVE (SECP256K1)
        :type curve: ec.EllipticCurve
        """
        if not aes_pass:
            raise ValueError("Invalid EcSigner: aes_pass cannot be empty")
        self._alg = ec.ECDSA(SHA256())
        self._curve = None
        self._pem_encryption = None

        if pkey and pub:
            self._pub = pub
            self._pk = pkey
            self._load_ec_key(pub, aes_pass)
        else:
            if curve is None:
                curve = kWALLET_CURVE
            self._make_ec_key(aes_pass, curve)

    def _make_ec_key(self, aes_pass: str, curve: ec.EllipticCurve):
        """Create a keypair on a given curve to initialize this EcSigner with.

        :param aes_pass: aes key to decrypt/encrypt the PEM file with; this is required
        :type aes_pass: str
        :param curve: elliptic curve to use in generating the key
        :type curve: ec.EllipticCurve
        """
        try:
            self._curve = curve
            ec_key = ec.generate_private_key(self._curve, backend=default_backend())
            self._pem_encryption = sz.BestAvailableEncryption(bytes(aes_pass, "utf-8"))
            self._pk = ec_key.private_bytes(
                encoding=sz.Encoding.PEM,
                format=sz.PrivateFormat.PKCS8,
                encryption_algorithm=self._pem_encryption,
            )

            self._pub = ec_key.public_key()
        except Exception as e:
            raise RuntimeError(
                f"Invalid EcSigner: failed to generate EC key-pair ({e})"
            )

    def _load_ec_key(self, pub: str or Address, aes_pass: str):
        """Load a keypair from the given private key and aes key,
        and verify that its public address matches the given one

        :param pub: the given public key, to compare against the public key generated from the given private key
        :type pub: str
        :param aes_pass: aes key to decrypt/encrypt the PEM file with; this is required
        :type aes_pass: str
        """
        if (
            len(self._pub) == kWALLET_ADDR_SIZE * 2
            or len(self._pub) == kWALLET_ADDR_SIZE
        ):
            self._curve = kWALLET_CURVE
        elif len(self._pub) == kNODE_ADDR_SIZE * 2 or len(self._pub) == kNODE_ADDR_SIZE:
            self._curve = kNODE_CURVE
        else:
            raise ValueError(f"Invalid EcSigner: bad public key length ({len(pub)})")
        if self._curve is None:
            raise ValueError("Invalid EcSigner: failed to generate ec_group")

        # Make private and public keys from the private value + curve
        self._pk = sz.load_pem_private_key(
            self._pk, password=bytes(aes_pass, "utf-8"), backend=default_backend()
        )

        self._pem_encryption = None
        self._pub = self._pk.public_key()

        pub_addr = pub if isinstance(pub, Address) else Address(pub)
        if self.get_signer_addr() != pub_addr:
            raise RuntimeError("Invalid EcSigner: could not reproduce public key")

    def get_pkey(self) -> str:
        """
        :return: this EcSigner's encrypted private key in string form, without PEM prefix/suffix or newlines
        :rtype: str
        """
        return self._pk.decode("utf-8")[kPEM_PREFIX_SIZE:-kPEM_SUFFIX_SIZE].replace(
            "\n", ""
        )

    def get_pubkey(self) -> str:
        """
        :return: this EcSigner's public key as a hex string
        :rtype: str
        """
        return (
            self._pub.public_bytes(sz.Encoding.X962, sz.PublicFormat.CompressedPoint)
            .hex()
            .upper()
        )

    def get_signer_addr(self) -> Address:
        """
        :return: this EcSigner's public key as an Address object
        :rtype: Address
        """
        return Address(self.get_pubkey())

    def sign(self, msg: bytes, verify: bool = True) -> bytes:
        """Signs and verifies the given bytes using the keypair given/generated on construction, and the
        ec.ECDSA(SHA256()) algorithm

        :param msg: the binary data to sign
        :type msg: bytes
        :param verify: if True, verify the signature
        :type verify: bool
        :return: a new signature for the given bytes
        :rtype: bytes
        """
        if not msg or not isinstance(msg, bytes):
            raise RuntimeError(f"Invalid signing: cannot sign msg type {type(msg)}")
        sig = self._pk.sign(msg, self._alg)
        if verify and not self.verify(sig, msg):
            raise RuntimeError("Invalid signing: failed sig verification")
        return sig

    def verify(self, sig, msg) -> bool:
        try:
            self._pub.verify(sig, msg, self._alg)
            return True
        except InvalidSignature:
            return False

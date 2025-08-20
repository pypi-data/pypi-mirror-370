import base64
import binascii
import datetime
from enum import Enum

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AES_128 = algorithms.AES128
KEY_SIZE = int(AES_128.block_size / 8)


class SearchCriteria(Enum):
    TRACKING_CODE = 'T'
    REFERENCE_NUMBER = 'R'


class CepGenerator(object):
    def __init__(self, hex_key: str):
        cleaned_hex_key = hex_key.replace(':', '')
        raw_key = binascii.unhexlify(cleaned_hex_key)

        self.key = raw_key[:KEY_SIZE]
        self.iv = raw_key[KEY_SIZE:]

    def generate_cep(
        self,
        date: datetime.datetime,
        search_criteria: SearchCriteria,
        search_value: str,
        origin_bank_code: str,
        receiver_bank_code: str,
        account_number: str,
        amount: float,
    ) -> str:
        formatted_date = self._format_date(date)
        string = '{0}|{1}|{2}|{3}|{4}|{5}|{6}'.format(
            formatted_date,
            search_criteria.value,
            search_value,
            origin_bank_code,
            receiver_bank_code,
            account_number,
            amount,
        )

        return self._encrypt_string(string)

    def decrypt_string(self, encrypted_data_base64: str) -> str:  # noqa: WPS210
        encrypted_data = base64.b64decode(encrypted_data_base64)
        decryptor = self.decryptor()

        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = self.unpadder
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data.decode()

    def encryptor(self, backend=None):
        return self.cipher(backend=backend).encryptor()

    def decryptor(self, backend=None):
        return self.cipher(backend=backend).decryptor()

    def cipher(self, backend=None):
        return Cipher(
            AES_128(self.key),
            modes.CBC(self.iv),
            backend=backend or default_backend(),
        )

    @property
    def padder(self):
        return self.padding.padder()

    @property
    def unpadder(self):
        return self.padding.unpadder()

    @property
    def padding(self):
        return padding.PKCS7(AES_128.block_size)

    def _format_date(self, date: datetime.datetime) -> str:
        return date.strftime('%Y%m%d')

    def _encrypt_string(self, string: str) -> str:  # noqa: WPS210
        encryptor = self.encryptor()

        padder = self.padder
        padded_data = padder.update(string.encode()) + padder.finalize()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_data_base64 = base64.b64encode(encrypted_data)

        return encrypted_data_base64.decode()

import base64
import codecs

from Crypto.Cipher import AES


class AesCipher(object):

    def __init__(self, key, iv):
        self.bs = AES.block_size
        self.key = key
        self.iv = iv

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


def decrypt_script(encrypted_script: str,
                   aes_key):
    try:
        # The init vector is appended before the encrypted script (Length = 32)
        key_bytes = codecs.decode(aes_key, 'hex_codec')
        iv_bytes = codecs.decode(encrypted_script[:32], 'hex_codec')
        cipher = AesCipher(key=key_bytes, iv=iv_bytes)
        return cipher.decrypt(encrypted_script[32:])
    except Exception:
        message = f'An error happened while decoding the inputs sent by Kawa. '
        if not aes_key:
            message += 'No aes key seem to be defined'
        elif len(aes_key) < 10:
            message += f'The aes key seems to be wrong: {aes_key}'
        else:
            aes_key_with_only_first_and_last_three = aes_key[:3] + '*' * (len(aes_key) - 6) + aes_key[-3:]
            message += f'Check the aes key is the same as in kawa: {aes_key_with_only_first_and_last_three}'
        raise Exception(message)

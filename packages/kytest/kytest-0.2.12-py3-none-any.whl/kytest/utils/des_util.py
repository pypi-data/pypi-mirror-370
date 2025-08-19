"""
pip install pycryptodome==3.14.1
"""
from Crypto.Cipher import AES
import base64


class KDES(object):
    """加解密方法合集"""

    def __init__(self, key, cont, _type="aes"):
        self._type = _type
        self.key = key
        self.src = cont

    @staticmethod
    def aes_encrypt(key, content):
        """
        aes加密
        @param key: 固定的16位秘钥
        @param content: 明文信息
        @return: 密文信息
        """
        aes = AES.new(str.encode(key), AES.MODE_ECB)
        encode_pwd = str.encode(content.rjust(16, '@'))
        encrypt_str = str(base64.encodebytes(aes.encrypt(encode_pwd)), encoding='utf-8')
        return encrypt_str

    @staticmethod
    def aes_decrypt(key, content):
        """
        aes解密
        @param key: 加密时传入的16位秘钥
        @param content: 密文信息
        @return: 明文信息
        """
        aes = AES.new(str.encode(key), AES.MODE_ECB)
        decrypt_str = (aes.decrypt(base64.decodebytes(content.encode(encoding='utf-8'))).decode().replace('@', ''))
        return decrypt_str

    def encrypt(self):
        if self._type == "aes":
            return self.aes_encrypt(self.key, self.src)

    def decrypt(self):
        if self._type == "aes":
            return self.aes_decrypt(self.key, self.src)


if __name__ == '__main__':
    KDES("xx", "yy").decrypt()
    pass




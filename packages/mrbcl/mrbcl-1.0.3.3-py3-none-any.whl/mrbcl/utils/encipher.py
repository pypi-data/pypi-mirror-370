from Crypto.Cipher import AES
from gmssl import sm4
from mrbcl.utils.common import base64_encode, base64_decode
from typing import Union
from Crypto.Random import get_random_bytes


class AesUtil:
    """
    AES加解密
    """

    @staticmethod
    def encrypt_cbc(plaintext: Union[str, bytes], key: Union[str, bytes], iv: Union[str, bytes]) -> bytes:
        """
        加密
        :param plaintext: 待加密数据(字符串或字节)
        :param key: 密钥(字符串或字节)
        :param iv: 偏移向量(字符串或字节)
        :return: 加密后二进制数据
        """
        # 密钥和偏移向量必须是字节类型
        if isinstance(key, str):
            key = key.encode('utf8')
        if isinstance(iv, str):
            iv = iv.encode('utf8')
        # 待加密字符串必须是字节类型
        if isinstance(plaintext, str):
            # 字符串补位
            data = AesUtil.pad(plaintext)
            plaintext = data.encode('utf8')
        # 初始化加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 加密后得到的是bytes类型的数据
        encrypt_bytes = cipher.encrypt(plaintext)
        return encrypt_bytes

    @staticmethod
    def decrypt_cbc(cipher_bytes: bytes, key: Union[str, bytes], iv: Union[str, bytes]) -> str:
        """
        解密
        :param cipher_bytes: 加密二进制数据
        :param key: 密钥(字符串或字节)
        :param iv: 偏移向量(字符串或字节)
        :return: 解密后字符串
        """
        # 密钥和偏移向量必须是字节类型
        if isinstance(key, str):
            key = key.encode('utf8')
        if isinstance(iv, str):
            iv = iv.encode('utf8')
        # 初始化加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 解密
        text_decrypted = cipher.decrypt(cipher_bytes)
        # 去补位
        text_decrypted = AesUtil.un_pad(text_decrypted)
        # 对byte字符串按utf-8进行解码
        plaintext = text_decrypted.decode('utf8')
        return plaintext

    @staticmethod
    def pad(s: str) -> str:
        """
        字符串补位,填充16字节块
        :param s: 待处理字符串
        :return: 补位后的字符串
        """
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    @staticmethod
    def un_pad(s: bytes) -> bytes:
        """
        移除 PKCS#7 填充：最后一个字节表示填充字节数
        :param s: 待处理数据
        :return:
        """
        return s[0:-s[-1]]

    @staticmethod
    def generate_key() -> bytes:
        """
        生成AES CBC模式所需的16字节密钥
        :return: 16字节的密钥
        """
        return get_random_bytes(16)


    @staticmethod
    def generate_iv() -> bytes:
        """
        生成AES CBC模式所需的16字节偏移向量
        :return: 16字节的偏移向量
        """
        return get_random_bytes(16)

class Sm4Util:
    """
    SM4加解密
    """

    @staticmethod
    def encrypt_ecb(plaintext: Union[str, bytes], key: Union[str, bytes]) -> bytes:
        """
        加密
        :param plaintext: 待加密数据(字符串或字节)
        :param key: 密钥(字符串或字节)
        :return: 二进制加密数据
        """
        # 待加密数据必须是字节类型
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf8')
        # 密钥必须是字节类型
        if isinstance(key, str):
            key = key.encode('utf8')
        sm4_alg = sm4.CryptSM4()  # 实例化sm4
        sm4_alg.set_key(key, sm4.SM4_ENCRYPT)  # 设置密钥
        ret_bytes = sm4_alg.crypt_ecb(plaintext)  # 开始加密,bytes类型，ecb模式
        return ret_bytes

    @staticmethod
    def decrypt_ecb(cipher_bytes: bytes, key: Union[str, bytes]) -> str:
        """
        解密
        :param cipher_bytes: 加密二进制数据
        :param key: 密钥(字符串或字节)
        :return: 解密后字符串
        """
        # 密钥必须是字节类型
        if isinstance(key, str):
            key = key.encode('utf8')
        sm4_alg = sm4.CryptSM4()  # 实例化sm4
        sm4_alg.set_key(key, sm4.SM4_DECRYPT)  # 设置密钥
        ret_bytes = sm4_alg.crypt_ecb(cipher_bytes)  # 开始解密。十六进制类型,ecb模式
        plaintext = ret_bytes.decode('utf8')
        return plaintext

    @staticmethod
    def generate_key() -> bytes:
        """
        生成SM4加密所需的16字节密钥
        :return: 16字节的密钥
        """
        return get_random_bytes(16)


if __name__ == '__main__':
    text = "123"
    aes_key = "91a055ac42b41132"
    aes_iv = "b5a836c453b982a2"
    # aes_key = AesUtil.generate_key()
    # aes_iv = AesUtil.generate_iv()
    # print("AES密钥===", hex_encode(aes_key))
    # print("AES偏移向量===", hex_encode(aes_iv))
    aes_cipher_bytes = AesUtil.encrypt_cbc(text, aes_key, aes_iv)
    aes_ciphertext = base64_encode(aes_cipher_bytes)
    print("AES加密后===", aes_ciphertext)
    aes_plaintext = AesUtil.decrypt_cbc(base64_decode(aes_ciphertext, True), aes_key, aes_iv)
    print("AES解密后===", aes_plaintext)

    sm4_key = "86C63180C2806ED1"
    # sm4_key = Sm4Util.generate_key()
    # print("SM4密钥===", hex_encode(sm4_key))
    sm4_cipher_bytes = Sm4Util.encrypt_ecb(text, sm4_key)
    sm4_ciphertext = base64_encode(sm4_cipher_bytes)
    print("SM4加密后===", sm4_ciphertext)
    sm4_plaintext = Sm4Util.decrypt_ecb(base64_decode(sm4_ciphertext, True), sm4_key)
    print("SM4解密后===", sm4_plaintext)

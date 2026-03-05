"""
加密管理模块
使用 PBKDF2HMAC 从用户密码派生 AES-256 密钥，通过 Fernet 对文件内容进行加密/解密
密钥派生所用的盐在注册时随机生成，存储于数据库，确保每个用户独立且不可预测
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# PBKDF2 迭代次数（满足 OWASP 2023 建议的 600,000 次）
PBKDF2_ITERATIONS = 600000
# 派生密钥长度（AES-256 需要 32 字节）
KEY_LENGTH = 32


class CryptoManager:
    """
    加密管理器：负责密钥派生及文件内容的加密与解密
    """

    def __init__(self, password: str, crypto_salt: bytes):
        """
        初始化加密管理器
        :param password: 用户明文密码
        :param crypto_salt: 注册时随机生成并存储在数据库中的盐（32 字节）
        """
        self._fernet = self._build_fernet(password, crypto_salt)

    def _build_fernet(self, password: str, salt: bytes) -> Fernet:
        """
        根据密码和随机盐派生 Fernet 密钥
        :param password: 明文密码
        :param salt: 随机盐
        :return: Fernet 实例
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> bytes:
        """
        加密文本内容
        :param plaintext: 明文字符串（UTF-8）
        :return: 加密后的字节串
        """
        return self._fernet.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> str:
        """
        解密字节串
        :param ciphertext: 密文字节串
        :return: 解密后的明文字符串
        :raises: cryptography.fernet.InvalidToken 当密钥不匹配时
        """
        return self._fernet.decrypt(ciphertext).decode("utf-8")

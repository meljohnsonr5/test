"""
用户管理模块
使用 SQLite 存储用户信息，密码通过 hashlib + 随机盐进行哈希，不存明文
每个用户注册时生成一个随机 crypto_salt，用于后续的文件加密密钥派生
"""

import hashlib
import os
import sqlite3


# 数据库文件路径
DB_PATH = "users.db"
# 哈希算法
HASH_ALGORITHM = "sha256"
# 盐长度（字节）
SALT_LENGTH = 32
# 最短密码长度
MIN_PASSWORD_LENGTH = 6
# PBKDF2 迭代次数（满足 OWASP 2023 建议：PBKDF2-HMAC-SHA256 使用 600,000 次）
PBKDF2_ITERATIONS = 600000


class UserManager:
    """
    用户管理器：负责用户注册、登录验证及加密盐的存取
    """

    def __init__(self, db_path: str = DB_PATH):
        """
        初始化用户管理器，确保数据库和表已创建
        :param db_path: SQLite 数据库文件路径
        """
        self._db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """初始化数据库，创建用户表（如不存在）"""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT    NOT NULL UNIQUE,
                    salt        TEXT    NOT NULL,
                    password    TEXT    NOT NULL,
                    crypto_salt TEXT    NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> str:
        """
        使用 PBKDF2-HMAC-SHA256 对密码进行哈希
        :param password: 明文密码
        :param salt: 随机盐（bytes）
        :return: 十六进制哈希字符串
        """
        dk = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return dk.hex()

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        注册新用户
        :param username: 用户名
        :param password: 明文密码
        :return: (成功标志, 消息)
        """
        username = username.strip()
        if not username:
            return False, "用户名不能为空"
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"密码长度至少 {MIN_PASSWORD_LENGTH} 位"

        # 密码哈希盐（用于验证登录）
        salt = os.urandom(SALT_LENGTH)
        hashed = self._hash_password(password, salt)
        # 加密密钥派生盐（用于文件加密，与密码哈希盐分开）
        crypto_salt = os.urandom(SALT_LENGTH)

        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, salt, password, crypto_salt) VALUES (?, ?, ?, ?)",
                    (username, salt.hex(), hashed, crypto_salt.hex()),
                )
                conn.commit()
            return True, "注册成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在，请换一个用户名"
        except Exception as exc:  # noqa: BLE001
            return False, f"注册失败：{exc}"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        验证用户登录
        :param username: 用户名
        :param password: 明文密码
        :return: (成功标志, 消息)
        """
        username = username.strip()
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT salt, password FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
        except Exception as exc:  # noqa: BLE001
            return False, f"数据库错误：{exc}"

        if row is None:
            return False, "用户名不存在"

        salt = bytes.fromhex(row["salt"])
        hashed = self._hash_password(password, salt)
        if hashed != row["password"]:
            return False, "密码错误"

        return True, "登录成功"

    def get_crypto_salt(self, username: str) -> bytes | None:
        """
        获取用户注册时生成的加密密钥派生盐
        :param username: 用户名
        :return: 盐的字节串，用户不存在时返回 None
        """
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT crypto_salt FROM users WHERE username = ?",
                    (username.strip(),),
                ).fetchone()
            if row is None:
                return None
            return bytes.fromhex(row["crypto_salt"])
        except Exception:  # noqa: BLE001
            return None

    def user_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在
        :param username: 用户名
        :return: True 表示存在
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE username = ?", (username.strip(),)
            ).fetchone()
        return row is not None

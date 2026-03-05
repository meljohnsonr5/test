"""
文件管理模块
负责加密文件的创建、读取、保存、删除操作
文件以加密格式存储在 data/<username>/ 目录下
"""

import os
from datetime import datetime
from typing import Optional

from app.crypto_manager import CryptoManager


# 加密文件存储根目录
DATA_ROOT = "data"
# 加密文件扩展名
ENCRYPT_EXT = ".enc"


class FileManager:
    """
    文件管理器：管理用户的加密文件（增删改查）
    """

    def __init__(self, username: str, crypto: CryptoManager):
        """
        初始化文件管理器
        :param username: 当前登录用户名
        :param crypto: 加密管理器实例
        """
        self._username = username
        self._crypto = crypto
        self._user_dir = os.path.join(DATA_ROOT, username)
        os.makedirs(self._user_dir, exist_ok=True)

    def _file_path(self, filename: str) -> str:
        """获取文件的完整磁盘路径"""
        # 确保文件名有正确扩展名
        if not filename.endswith(ENCRYPT_EXT):
            filename = filename + ENCRYPT_EXT
        return os.path.join(self._user_dir, filename)

    def _display_name(self, filename: str) -> str:
        """将磁盘文件名转换为显示名称（去掉 .enc 后缀）"""
        if filename.endswith(ENCRYPT_EXT):
            return filename[: -len(ENCRYPT_EXT)]
        return filename

    def list_files(self) -> list[dict]:
        """
        列出用户目录下所有加密文件
        :return: 文件信息列表，每项包含 name（显示名）、filename（磁盘名）、modified（修改时间）
        """
        result = []
        try:
            for fname in sorted(os.listdir(self._user_dir)):
                if not fname.endswith(ENCRYPT_EXT):
                    continue
                fpath = os.path.join(self._user_dir, fname)
                mtime = os.path.getmtime(fpath)
                modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                result.append(
                    {
                        "name": self._display_name(fname),
                        "filename": fname,
                        "modified": modified,
                    }
                )
        except OSError:
            pass
        return result

    def read_file(self, filename: str) -> Optional[str]:
        """
        读取并解密文件内容
        :param filename: 文件名（显示名或磁盘名均可）
        :return: 解密后的文本内容，失败返回 None
        """
        fpath = self._file_path(filename)
        try:
            with open(fpath, "rb") as f:
                ciphertext = f.read()
            return self._crypto.decrypt(ciphertext)
        except FileNotFoundError:
            return None
        except Exception:  # noqa: BLE001
            return None

    def save_file(self, filename: str, content: str) -> tuple[bool, str]:
        """
        加密并保存文件内容
        :param filename: 文件名（显示名）
        :param content: 明文内容
        :return: (成功标志, 消息)
        """
        filename = filename.strip()
        if not filename:
            return False, "文件名不能为空"
        # 禁止路径遍历
        safe_name = os.path.basename(filename)
        if not safe_name:
            return False, "文件名无效"

        fpath = self._file_path(safe_name)
        try:
            ciphertext = self._crypto.encrypt(content)
            with open(fpath, "wb") as f:
                f.write(ciphertext)
            return True, "保存成功"
        except Exception as exc:  # noqa: BLE001
            return False, f"保存失败：{exc}"

    def delete_file(self, filename: str) -> tuple[bool, str]:
        """
        删除指定文件
        :param filename: 文件名（显示名或磁盘名均可）
        :return: (成功标志, 消息)
        """
        fpath = self._file_path(filename)
        try:
            os.remove(fpath)
            return True, "删除成功"
        except FileNotFoundError:
            return False, "文件不存在"
        except Exception as exc:  # noqa: BLE001
            return False, f"删除失败：{exc}"

    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在
        :param filename: 文件名（显示名）
        :return: True 表示存在
        """
        return os.path.isfile(self._file_path(filename))

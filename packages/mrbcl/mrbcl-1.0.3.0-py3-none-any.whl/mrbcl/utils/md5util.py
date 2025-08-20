import hashlib
from typing import Optional

def md5_string(input_str: str, encoding: str = 'utf-8') -> str:
    """
    计算字符串的MD5哈希值
    :param input_str: 输入的字符串
    :param encoding: 字符串编码，默认为utf-8
    :return: MD5哈希值（十六进制字符串）
    """
    md5 = hashlib.md5()
    md5.update(input_str.encode(encoding))
    return md5.hexdigest()

def md5_string_bytes(input_str: str, encoding: str = 'utf-8') -> bytes:
    """
    计算字符串的MD5哈希值并返回字节形式
    :param input_str: 输入的字符串
    :param encoding: 字符串编码，默认为utf-8
    :return: MD5哈希值（字节形式）
    """
    md5 = hashlib.md5()
    md5.update(input_str.encode(encoding))
    return md5.digest()

def md5_bytes(input_bytes: bytes) -> str:
    """
    计算字节的MD5哈希值
    :param input_bytes: 输入的字节
    :return: MD5哈希值（十六进制字符串）
    """
    md5 = hashlib.md5()
    md5.update(input_bytes)
    return md5.hexdigest()

def md5_bytes_bytes(input_bytes: bytes) -> bytes:
    """
    计算字节的MD5哈希值并返回字节形式
    :param input_bytes: 输入的字节
    :return: MD5哈希值（字节形式）
    """
    md5 = hashlib.md5()
    md5.update(input_bytes)
    return md5.digest()

def md5_file(file_path: str) -> Optional[str]:
    """
    计算文件的MD5哈希值
    :param file_path: 文件的路径
    :return: MD5哈希值（十六进制字符串），若文件打开失败则返回None
    """
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception:
        return None

def md5_file_bytes(file_path: str) -> Optional[bytes]:
    """
    计算文件的MD5哈希值并返回字节形式
    :param file_path: 文件的路径
    :return: MD5哈希值（字节形式），若文件打开失败则返回None
    """
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                md5.update(chunk)
        return md5.digest()
    except Exception:
        return None
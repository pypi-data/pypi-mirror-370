import base64
import binascii
import codecs
import os
import sys
from typing import Union
import xml.etree.ElementTree as et


def parse_xml_config(xml_file_path: str, element_name: str) -> dict[str, str]:
    """
    解析XML
    :param xml_file_path: xml文件路径
    :param element_name: 节点名称
    :return:
    """
    # 解析 XML 文件
    tree = et.parse(xml_file_path)
    root = tree.getroot()

    # 获取数据库连接串参数
    params_obj = {}
    for elem in root.findall(f".//{element_name}/*"):
        params_obj[elem.tag] = elem.text

    return params_obj


def get_file_path(relative_path: str) -> str:
    """
    获取资源绝对路径（根据运行环境自动切换路径）
    :param relative_path: 资源相对路径
    :return:
    """
    if getattr(sys, 'frozen', False):  # 打包环境
        if hasattr(sys, '_MEIPASS'):  # --onefile 模式
            base_path = sys._MEIPASS  # 临时解压目录
        else:  # --onedir 模式
            base_path = os.path.dirname(sys.executable)  # 可执行文件所在目录
    else:  # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_path, relative_path))  # 返回实际路径


def base64_encode(raw_data: Union[str, bytes, bytearray], ret_bytes: bool = False, urlsafe: bool = False, charset: str = "utf-8") -> Union[str, bytes]:
    """
    Base64加密
    :param raw_data: 待加密数据
    :param ret_bytes: 是否返回byte数据
    :param urlsafe: 是否使用urlsafe模式, 此模式会将+替换为-, /替换为_
    :param charset: 字符编码: utf-8,gbk
    :return: 加密后数据
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    if urlsafe:
        base64_str = base64.urlsafe_b64encode(raw_data)
    else:
        base64_str = base64.b64encode(raw_data)
    if not ret_bytes:
        base64_str = base64_str.decode(charset)
    return base64_str


def base64_decode(raw_data: Union[str, bytes, bytearray], ret_bytes: bool = False, urlsafe: bool = False, charset: str = "utf-8") -> Union[str, bytes]:
    """
    Base64解密
    :param raw_data: 待解密数据
    :param ret_bytes: 是否返回byte数据
    :param urlsafe: 是否使用urlsafe模式, 加密串存在-和_时使用
    :param charset:  字符编码: utf-8,gbk 仅在ret_bytes=False时生效
    :return: 解密后数据
    """
    if urlsafe:
        raw_str = base64.urlsafe_b64decode(raw_data)
    else:
        raw_str = base64.b64decode(raw_data)
    if not ret_bytes:
        raw_str = raw_str.decode(charset)
    return raw_str


def unicode_encode(raw_data: str, charset: str = "utf-8") -> str:
    """
    unicode编码
    :param raw_data: 原始数据
    :param charset: 字符编码
    :return:
    """
    return codecs.encode(raw_data, 'unicode_escape').decode(charset)


def unicode_decode(raw_data: Union[str, bytes, bytearray], charset: str = "utf-8") -> str:
    """
    unicode解码
    :param raw_data: 原始数据
    :param charset: 字符编码
    :return:
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    elif isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data
    return codecs.decode(raw_data, 'unicode_escape')


def hex_encode(raw_data: Union[str, bytes, bytearray], ret_bytes: bool = False, charset: str = "utf8") -> Union[str, bytes]:
    """
    16进制编码
    :param raw_data: 原始数据
    :param ret_bytes: 是否返回字节数组
    :param charset: 返回字符串编码
    :return:
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    elif isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data
    hex_bytes = binascii.hexlify(raw_data)
    if ret_bytes is True:
        return hex_bytes
    return hex_bytes.decode(charset)


def hex_decode(hex_str: str, ret_bytes: bool = False, charset: str = "utf8") -> Union[str, bytes]:
    """
    16进制解码
    :param hex_str: 16进制字符串
    :param ret_bytes: 是否返回字节数组
    :param charset: 返回字符串编码
    :return:
    """
    hex_bytes = binascii.unhexlify(hex_str)
    if ret_bytes is True:
        return hex_bytes
    return hex_bytes.decode(charset)

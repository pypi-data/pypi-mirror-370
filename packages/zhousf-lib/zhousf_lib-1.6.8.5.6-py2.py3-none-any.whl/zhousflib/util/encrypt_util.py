# -*- coding:utf-8 -*-
# Author:      zhousf
# Description:  加密工具
# pip install pycryptodome -i https://pypi.mirrors.ustc.edu.cn/simple/
import base64
import hashlib
import random
import string

from Crypto.Cipher import AES


class AESUtil(object):
    def __init__(self, key, mode):
        self.key = key
        self.mode = mode
        self.aes = AES.new(key=self.zero_padding_16(self.key), mode=self.mode)

    @staticmethod
    def zero_padding_16(text):
        """
        128位，0填充
        :param text:
        :return:
        """
        while len(text) % 16 != 0:
            text += '\0'
        return str.encode(text)

    def encrypt(self, text):
        """
        加密
        :param text:
        :return: 加密后的字符串
        """
        text_byte = self.zero_padding_16(text)
        return str(base64.encodebytes(self.aes.encrypt(text_byte)), encoding='utf8').replace('\n', '')

    def decrypt(self, text):
        """
        解密
        :param text:
        :return: 解密后的字符串
        """
        text_byte = bytes(text, encoding='utf8')
        return str(self.aes.decrypt(base64.decodebytes(text_byte)).rstrip(b'\0').decode("utf8"))


def md5(text):
    return hashlib.md5(text.encode("utf8")).hexdigest()


def sha256(value):
    """
    sha256加密
    return:加密结果转成16进制字符串形式
    """
    hash_obj = hashlib.sha256()
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def pwd_generator(num=32):
    """
    密码生成器
    :param num: 密码位数
    :return:
    """
    letters = string.ascii_letters + string.digits + "@#%&+="
    key = random.sample(letters, num)
    pwd = "".join(key)
    return pwd


if __name__ == "__main__":
    print(pwd_generator(32))
    # api_key = "7uGt@UwQofA=DO4k6F%+&PibIszV9X2m"
    # api_secret = "bp2q=jtJa8P#dHOzLKFBGg6n1UNmwZTy"
    # req_id = "157078081781"
    # unionText = api_key + req_id + api_secret
    # print("加密前:{}".format(unionText))
    # encryptedText = sha256(unionText)
    # print("加密后:{}".format(encryptedText))

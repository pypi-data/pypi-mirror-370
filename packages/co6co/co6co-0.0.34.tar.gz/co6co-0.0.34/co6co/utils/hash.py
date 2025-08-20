# -*- coding: utf-8 -*-
import hashlib,os ,string 

def enbase642(content:str):
    """
    base64  加密 为什么不对
    """
    content=content.encode()
    # base64字符集
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
 
    # 将文件内容按6位分组，并在末尾补0
    groups = [content[i:i+3] for i in range(0, len(content), 3)]
    encoded_groups = []
    for group in groups:
        # 获取每个字符的ASCII码，转为二进制
        binary_group = ''.join(format(byte, '08b') for byte in group)
 
        # 根据6位进行切片并加密
        encodings = [base64_chars[int(binary_group[i:i+6], 2)] for i in range(0, len(binary_group), 6)]
 
        # 处理补位（如果不是3字节的整数倍）
        if len(encodings) < 4:
            encodings.extend(['='] * (4 - len(encodings)))
 
        encoded_groups.append(''.join(encodings))
    encoded_string = ''.join(encoded_groups) 
    return encoded_string

base64_charset = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
def enbase64(data:str|bytes):
    """
    将bytes类型编码为base64
    :param origin_bytes:需要编码的bytes
    :return:base64字符串
    """
    if type(data)==str: data=data.encode()
    # 将每一位bytes转换为二进制字符串
    base64_bytes = ['{:0>8}'.format(str(bin(b)).replace('0b', '')) for b in data]

    resp = ''
    nums = len(base64_bytes) // 3
    remain = len(base64_bytes) % 3

    integral_part = base64_bytes[0:3 * nums]
    while integral_part:
        # 取三个字节，以每6比特，转换为4个整数
        tmp_unit = ''.join(integral_part[0:3])
        tmp_unit = [int(tmp_unit[x: x + 6], 2) for x in [0, 6, 12, 18]]
        # 取对应base64字符
        resp += ''.join([base64_charset[i] for i in tmp_unit])
        integral_part = integral_part[3:]

    if remain:
        # 补齐三个字节，每个字节补充 0000 0000
        remain_part = ''.join(base64_bytes[3 * nums:]) + (3 - remain) * '0' * 8
        # 取三个字节，以每6比特，转换为4个整数
        # 剩余1字节可构造2个base64字符，补充==；剩余2字节可构造3个base64字符，补充=
        tmp_unit = [int(remain_part[x: x + 6], 2) for x in [0, 6, 12, 18]][:remain + 1]
        resp += ''.join([base64_charset[i] for i in tmp_unit]) + (3 - remain) * '='

    return resp

def valid_base64_str(b_str):
    """
    = 存在的意义是为了补位 要是4个字符的倍数，如果不是4的倍数需要在结尾加上=
    验证是否为合法base64字符串
    :param b_str: 待验证的base64字符串
    :return:是否合法
    """ 
    if len(b_str) % 4: 
        return False

    for m in b_str:
        if m not in base64_charset: 
            return False
    return True

def debase64(data:str|bytes,encodeing:str|None="utf-8") ->str|bytes:
    """
    解码base64字符串
    :param base64_str:base64字符串
    :return:解码后的bytearray；若入参不是合法base64字符串，返回空bytearray
    """
    #if not valid_base64_str(base64_str):
    #    return bytearray()
    content=data
    if type(data)==bytes:content=data.decode(encodeing)

    # 对每一个base64字符取下标索引，并转换为6为二进制字符串
    base64_bytes = ['{:0>6}'.format(str(bin(base64_charset.index(s))).replace('0b', '')) for s in content if s != '=']
    resp = bytearray()
    nums = len(base64_bytes) // 4
    remain = len(base64_bytes) % 4
    integral_part = base64_bytes[0:4 * nums]

    while integral_part:
        # 取4个6位base64字符，作为3个字节
        tmp_unit = ''.join(integral_part[0:4])
        tmp_unit = [int(tmp_unit[x: x + 8], 2) for x in [0, 8, 16]]
        for i in tmp_unit:
            resp.append(i)
        integral_part = integral_part[4:]

    if remain:
        remain_part = ''.join(base64_bytes[nums * 4:])
        tmp_unit = [int(remain_part[i * 8:(i + 1) * 8], 2) for i in range(remain - 1)]
        for i in tmp_unit:
            resp.append(i) 
    if encodeing==None:return resp
    else:  return resp.decode(encodeing) 

def md5(plain_text:str)->str:
    """
    获取MD5摘要
    """
    return str_md5(plain_text)

def file_hash(file_path: str, hash_method) -> str:
    if not os.path.isfile(file_path): raise Exception(message=f"{file_hash} not exist") 
    h = hash_method()
    with open(file_path, 'rb') as f:
        while b := f.read(8192): h.update(b)
    return h.hexdigest() 

def str_hash(content: str, hash_method, encoding: str = 'UTF-8') -> str:
    return hash_method(content.encode(encoding)).hexdigest()


def file_md5(file_path: str) -> str:
    return file_hash(file_path, hashlib.md5)


def file_sha256(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha256)


def file_sha512(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha512)


def file_sha384(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha384)


def file_sha1(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha1)


def file_sha224(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha224)


def str_md5(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.md5, encoding)


def str_sha256(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.sha256, encoding)


def str_sha512(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.sha512, encoding)


def str_sha384(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.sha384, encoding)


def str_sha1(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.sha1, encoding)


def str_sha224(content: str, encoding: str = 'UTF-8') -> str:
    return str_hash(content, hashlib.sha224, encoding) 
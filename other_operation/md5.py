import hashlib


def cal_md5(file):  # 传入读取过的文件
    return hashlib.md5(file).hexdigest()
import os
import io
import sys
from md5 import *
import hashlib
import random


def cal_already_exists_pic_md5():
    file_md5 = []

    filenames = os.listdir('../pic/qcjj')
    for file_name in filenames:
        # print(file_name)
        with open('../pic/qcjj/' + file_name, 'rb') as fp:
            data = fp.read()
        file_md5.append(cal_md5(data))

    return file_md5


async def get_random_qcjj():
    img_list = os.listdir('../pic/qcjj/')
    img_local = '../pic/qcjj/' + random.choice(img_list)
    return img_local



if __name__ == '__main__':
    print(cal_already_exists_pic_md5())
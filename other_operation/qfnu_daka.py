# -*- coding: utf8 -*-
import requests
import smtplib
import time
import datetime

# 账号密码
info = {

    '2020416070': '123456Abc',
    '2020416059': 'Gz15615790976',
    '2020416018': 'Leng199443',
    '2019416714': '18037689wadsA',
    '2020416080': '123456789Qwe'

}
errorinfo = []
server = "http://xuegong.qfnu.edu.cn:8080"


def myHealth(user, pwd):
    s = requests.Session()  # 新建一个request对象
    data = {
        'username': user,
        'password': pwd,
        'type': 'student',
    }
    r = s.post('http://xuegong.qfnu.edu.cn:8080/authentication/login', json=data)  # 登录

    if r.json()['ok']:
        errorinfo.append(str(user) + ' 登陆成功')
    else:
        s.close()
        errorinfo.append(str(user) + ' 登陆失败')
        return
    # 健康信息
    data = {"home": "在校", "address": "山东省日照市东港区滨州路82号靠近曲阜师范大学日照校区", "keepInHome": "否", "keepInHomeDate": "null",
            "keepInHomeReasonSite": "null", "contact": "否", "contactType": "null", "infect": "否", "infectType": "null",
            "infectDate": "null", "familyNCP": "否", "familyNCPType": "null", "familyNCPDate": "null",
            "familyNCPRelation": "null", "cold": "否", "fever": "否", "feverValue": "", "cough": "否", "diarrhea": "否",
            "homeInHubei": "否", "arriveHubei": "无", "travel": "无", "remark": "无", "submitCount": 0, "contactDetail": "",
            "location": "山东省日照市东港区滨州路82号靠近曲阜师范大学日照校区", "naDetection": "是", "areaInfect": "否", "areaInfectType": "null",
            "areaInfectDate": "null", "areaInfectNumber": "null", "contactAH": "否", "contactAHDetail": "",
            "outProvinceBack14": "未出省", "naDetectionDate": str(datetime.datetime.today().year) + "-" + str(
            datetime.datetime.today().month) + "-" + str(datetime.datetime.today().day), "pharynxResult": "阴性",
            "anusResult": "阴性", "saDetection": "否", "lgMResult": "阴性", "lgGResult": "阴性", "saDetectionDate": "null",
            "vaccinationStatus": "已接种_完成第2剂"}
    r = s.post('http://xuegong.qfnu.edu.cn:8080/student/healthInfo/save', json=data)
    if r.json()['ok']:
        errorinfo.append(str(user) + ' 提交健康信息成功')
    else:
        errorinfo.append(str(user) + ' 提交健康信息失败：' + r.json()['message'])
    s.close()


def dk():
    for i in info.keys():
        myHealth(i, info[i])
    # print(errorinfo)
    res = errorinfo
    errorinfo.clear()
    return res

if __name__ == '__main__':
    dk()
    errorinfo.clear()
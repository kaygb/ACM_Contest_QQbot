import asyncio
import pprint
import time

from oj_api.global_pk import *


class CF(Contest):
    def __init__(self):
        self.HOST = "https://codeforces.com/api/"
        self.PATH = {
            "userRating": "user.rating",
            "contestList": "contest.list"
        }
        super().__init__()
        self.all_contest_list = []
        self.edu_list = []
        self.div1_list = []
        self.div2_list = []
        self.div3_list = []
        self.div4_list = []
        asyncio.run(self.get_contest_finshed())

    async def get_rating(self, name):
        def pd_color(rating):
            if rating < 1200:
                return "灰名隐藏大佬"
            if rating < 1400:
                return '绿名'
            if rating < 1600:
                return '青名'
            if rating < 1900:
                return '蓝名大佬'
            if rating < 2100:
                return '紫名巨巨'
            if rating < 2300:
                return '橙名'
            if rating < 2400:
                return '橙名'
            if rating < 3000:
                return '红名巨佬'
            else:
                return '黑红名神犇'

        url = self.HOST + self.PATH["userRating"]
        data = {
            "handle": name
        }
        self.updated_time = time.time()

        try:
            json_data = httpx.get(url, params=data).json()
            if json_data['status'] == "OK":
                json_data = json_data['result']
                if len(json_data) == 0:
                    return "该用户还未进行过比赛"

                # pprint.pprint(json_data[-1])

                final_contest = json_data[-1]
                # print(
                s = "“{}”是{}，当前rating为：{}".format(name, pd_color(int(final_contest['newRating'])),
                                                  final_contest['newRating'])
                # )
                return s
            else:
                logger.warning(json_data)
                return -1  # 表示请求失败
        except:
            return "程序出错，请稍后再试"

    async def get_contest(self):
        url = self.HOST + self.PATH["contestList"]
        data = {
            "gym": False
        }
        contest_url = "https://codeforces.com/contest/"
        json_data = httpx.get(url, params=data).json()
        if json_data['status'] == "OK":
            contest_list_all = list(json_data['result'])
            contest_list_lately = []

            for contest in contest_list_all:
                if contest['relativeTimeSeconds'] < 0:  # 小于0表示未来的比赛
                    contest_list_lately.append(contest)
                else:
                    break

            if len(contest_list_lately) == 0:
                # print("最近没有比赛~")
                return "最近没有比赛~", 0, 0
            else:
                contest_list_lately.sort(key=lambda x: (x['relativeTimeSeconds'], x['name']), reverse=True)  #
                # 先按照时间顺序排，然后按照名字排序（有的时候会出现12同时的情况，这样可以让div2在上面）

                contest = contest_list_lately[0]
                res = "下一场Codeforces比赛为：\n"
                res += "比赛名称：{}\n开始时间：{}\n持续时间：{}\n比赛地址：{}".format(
                    contest['name'],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(contest['startTimeSeconds']))),
                    "{}小时{:02d}分钟".format(contest['durationSeconds'] // 3600, contest['durationSeconds'] % 3600 // 60),
                    contest_url + str(contest['id'])
                )
                return res, int(contest['startTimeSeconds']), int(contest['durationSeconds'])

    async def get_all_finshed_contest(self):  # 获取所有的比赛json
        url = self.HOST + self.PATH["contestList"]
        data = {
            "gym": False
        }

        json_data = httpx.get(url, params=data).json()  # 向网站请求json文件

        return json_data

    async def get_contest_finshed(self):  # 获取近两年的cf比赛

        json_data = await self.get_all_finshed_contest()  # 向网站请求json文件

        if json_data['status'] == "OK":
            contest_list_all = list(json_data['result'])
            for contest in contest_list_all:
                if contest['relativeTimeSeconds'] > 0 and int(
                        time.time()) - 3 * 365 * 24 * 3600 <= contest['startTimeSeconds'] <= int(
                    time.time()) - 180 * 24 * 3600:  # 3年前到180天前
                    if (contest['type'] == 'CF' or contest['type'] == 'ICPC') and 'Codeforces' in contest['name']:  # 筛选常规的
                        self.all_contest_list.append(contest)
                        if 'Educational Codeforces Round' in contest['name']:
                            self.edu_list.append(contest)
                        elif 'Div. 3' in contest['name']:
                            self.div3_list.append(contest)
                        elif 'Div. 2' in contest['name']:
                            self.div2_list.append(contest)
                        elif 'Div. 1' in contest['name']:
                            self.div1_list.append(contest)
                        elif 'Div. 4' in contest['name']:
                            self.div4_list.append(contest)


    async def get_random_contest(self, type='normal'):
        if type == 'normal':
            id = random.randint(0, len(self.all_contest_list) - 1)
            contest = self.all_contest_list[id]
        if type == 'edu':
            id = random.randint(0, len(self.edu_list) - 1)
            contest = self.edu_list[id]
        if type == 'div1':
            id = random.randint(0, len(self.div1_list) - 1)
            contest = self.div1_list[id]
        if type == 'div2':
            id = random.randint(0, len(self.div2_list) - 1)
            contest = self.div2_list[id]
        if type == 'div3':
            id = random.randint(0, len(self.div3_list) - 1)
            contest = self.div3_list[id]
        if type == 'div4':
            id = random.randint(0, len(self.div4_list) - 1)
            contest = self.div4_list[id]

        res = "随机到的cf比赛为：\n" \
              "名称：{}\n" \
              "比赛地址：{}".format(contest['name'], "https://codeforces.com/contest/" + str(contest['id']))
        return res

    async def update_contest(self, flag=0):
        await super().update_contest(flag)
        await self.get_contest_finshed()


if __name__ == '__main__':
    # name = input()

    # asyncio.run(get_usr_rating(name))
    # while True:
    #     name = input()
    #     print(asyncio.run(get_usr_rating(name)))

    cf = CF()
    # logger.info(asyncio.run(cf.get_random_contest()))
    # logger.info(cf.contest_finshed_list)
    pprint.pprint(cf.div1_list)
    # get_contest()

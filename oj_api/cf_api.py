from oj_api.global_pk import *


class CF(Contest):
    def __init__(self):
        self.HOST = "https://codeforces.com/api/"
        self.PATH = {
            "userRating": "user.rating",
            "contestList": "contest.list"
        }
        super().__init__()
        self.contest_finshed_list = []
        asyncio.run(self.get_contest_finshed())


    async def get_rating(self, name):
        def pd_color(ratting):
            if ratting < 1200:
                return "灰名隐藏大佬"
            if ratting < 1400:
                return '绿名'
            if ratting < 1600:
                return '青名'
            if ratting < 1900:
                return '蓝名大佬'
            if ratting < 2100:
                return '紫名巨巨'
            if ratting < 2300:
                return '橙名'
            if ratting < 2400:
                return '橙名'
            if ratting < 2600:
                return '红名巨佬'
            else:
                return '黑红名神犇'

        url = self.HOST+self.PATH["userRating"]
        data = {
            "handle":name
        }
        self.updated_time = time.time()

        try:
            json_data = httpx.get(url,params=data).json()
            if json_data['status'] == "OK":
                json_data = json_data['result']
                if len(json_data) == 0:
                    return "该用户还未进行过比赛"

                # pprint.pprint(json_data[-1])

                final_contest = json_data[-1]
                # print(
                s = "“{}”是{}，当前ratting为：{}".format(name, pd_color(int(final_contest['newRating'])),
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
        json_data = httpx.get(url,params=data).json()
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
                contest_list_lately.sort(key=lambda x: (x['relativeTimeSeconds'], x['name']), reverse=True)

                contest = contest_list_lately[0]
                res = "下一场Codeforces比赛为：\n"
                res += "比赛名称：{}\n开始时间：{}\n持续时间：{}\n比赛地址：{}".format(
                    contest['name'],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(contest['startTimeSeconds']))),
                    "{}小时{:02d}分钟".format(contest['durationSeconds'] // 3600, contest['durationSeconds'] % 3600 // 60),
                    contest_url + str(contest['id'])
                )
                return res, int(contest['startTimeSeconds']), int(contest['durationSeconds'])


    async def get_contest_finshed(self):  # 获取近两年的cf比赛
        url = self.HOST + self.PATH["contestList"]
        data = {
            "gym": False
        }
        json_data = httpx.get(url, params=data).json()
        if json_data['status'] == "OK":
            contest_list_all = list(json_data['result'])
            for contest in contest_list_all:
                if contest['relativeTimeSeconds'] > 0 and contest['startTimeSeconds'] >= int(time.time()) - 2 * 365 * 24 * 3600:  # 两年的时间戳
                    if contest['type'] == 'CF' and 'Codeforces ' in contest['name']:
                        self.contest_finshed_list.append(contest)

    async def get_random_contest(self):
        id = random.randint(1, len(self.contest_finshed_list))
        contest = self.contest_finshed_list[id]
        res = "随机到的cf比赛为：\n" \
              "名称：{}\n" \
              "比赛地址：{}".format(contest['name'], "https://codeforces.com/contest/" + str(contest['id']))
        return res


if __name__ == '__main__':
    # name = input()
    name = "ING__"

    # asyncio.run(get_usr_rating(name))
    # while True:
    #     name = input()
    #     print(asyncio.run(get_usr_rating(name)))

    cf = CF()
    logger.info(asyncio.run(cf.get_random_contest()))
    logger.info(asyncio.run(cf.get_rating(name)))
    # get_contest()

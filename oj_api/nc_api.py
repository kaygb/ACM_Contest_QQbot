import pprint

from oj_api.global_pk import *


class NC(Contest):
    def __init__(self):
        self.HOST = "https://ac.nowcoder.com/acm/"
        self.PATH = {
            "contestList": "calendar/contest",
            "userRating": "contest/rating-index"
        }
        super().__init__()

    async def get_contest(self):
        res = []  # 存放数据
        now = datetime.datetime.now()
        try:
            now = now + relativedelta(months=-1)  # 减一为了保证第一次循环是当前月

            for _ in range(12):  # 如果处在月末可能当月没有比赛需要请求下一个月的
                now += relativedelta(months=1)  # 看看下个月的
                date = str(now.year) + '-' + str(now.month)  # 构造日期
                data = {
                    "token": "",
                    "month": date,
                    "_": str(int(time.time()) * 1000)
                }
                url = self.HOST + self.PATH["contestList"]
                json_data = httpx.get(url, params=data).json()  # 获取比赛json
                contest_data = json_data['data']
                for contest in contest_data:
                    if contest['ojName'] == 'NowCoder' \
                            and contest['startTime'] >= int(time.time()) * 1000 \
                            and ("专题" not in contest['contestName']):
                        if contest.__contains__('endTime') and contest.__contains__('startTime'):

                            during_time = (int(contest['endTime']) - int(contest['startTime'])) // 1000

                            res.append({
                                "contest_info": "比赛名称：{}\n" \
                                                "开始时间：{}\n" \
                                                "持续时间：{}\n" \
                                                "比赛地址：{}".format(
                                    contest['contestName'],
                                    time.strftime("%Y-%m-%d %H:%M:%S",
                                                  time.localtime(int(contest['startTime']) // 1000)),
                                    "{}小时{:02d}分钟".format(during_time // 3600, during_time % 3600 // 60),
                                    contest['link'][:-18]
                                ),
                                'begin_time': contest['startTime'] // 1000,
                                'during_time': during_time,
                            })

                            if len(res) > 4:  # 多获取一些，若oj长时间崩溃可以有更多的比赛信息轮换
                                break
                return res, res[0]['begin_time'], res[0]['during_time']
        except:
            # 如果请求失败就判断时候应当更换比赛信息
            return self.get_next_contest()

    async def get_rating(self, name):
        data = {
            "searchUserName": name
        }
        url = self.HOST + self.PATH["userRating"]
        zm = httpx.get(url, params=data).text
        xx = etree.fromstring(zm, parser=etree.HTMLParser())
        rating = xx.xpath('/html/body/div/div[2]/div/div/div[2]/table/tbody/tr/td[5]/span/text()')
        return "“{}”当前牛客rating为：{}".format(name, rating[0])


if __name__ == '__main__':
    nc = NC()
    # logger.info(nc.list)
    pprint.pprint(nc.list)
    # pprint.pprint(asyncio.run(()))
    # logger.debug(asyncio.run(nc.get_rating("ING__")))

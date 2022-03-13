from oj_api.global_pk import *
#from global_pk import *
class NC(Contest):
    def __init__(self):
        self.HOST = "https://ac.nowcoder.com/acm/"
        self.PATH = {
            "contestList": "calendar/contest",
            "userRating":"contest/rating-index"

        }
        super().__init__()

    async def get_contest(self):
        async def find():
            now = datetime.datetime.now()
            try:
                now = now + relativedelta(months=-1)
                for _ in range(12):
                    now = now + relativedelta(months=1)
                    date = str(now.year) + '-' + str(now.month)
                    data = {
                        "token":"",
                        "month":date,
                        "_":str(int(time.time()) * 1000)
                    }
                    url = self.HOST + self.PATH["contestList"]
                    json_data = httpx.get(url,params=data).json()
                    contest_data = json_data['data']
                    for contest in contest_data:
                        if contest['ojName'] == 'NowCoder' \
                                and contest['startTime'] >= int(time.time()) * 1000 \
                                and ("专题" not in contest['contestName']):
                            lately_contest = contest
                            if lately_contest.__contains__('endTime') and lately_contest.__contains__('startTime'):
                                durationSeconds = (int(lately_contest['endTime']) - int(
                                    lately_contest['startTime'])) // 1000
                                return lately_contest, durationSeconds  # 只获取马上要举行的牛客比赛
                    else:
                        return -2, 0
            except:
                logger.warning("发生错误")
                return -1

        lately_contest, durationSeconds = await find()

        if lately_contest == -1:
            return -1

        if lately_contest == -2:
            return "最近无比赛哦~", 0, 0

        res = "下一场牛客比赛为：\n" \
              "比赛名称：{}\n" \
              "开始时间：{}\n" \
              "持续时间：{}\n" \
              "比赛地址：{}".format(
            lately_contest['contestName'],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(lately_contest['startTime']) // 1000)),
            "{}小时{:02d}分钟".format(durationSeconds // 3600, durationSeconds % 3600 // 60),
            lately_contest['link']
        )

        return res, int(lately_contest['startTime'] // 1000), durationSeconds

    async def get_rating(self, name):
        data = {
            "searchUserName":name
        }
        url = self.HOST + self.PATH["userRating"]
        zm = httpx.get(url,params=data).text
        xx = etree.fromstring(zm, parser=etree.HTMLParser())
        rating = xx.xpath('/html/body/div/div[2]/div/div/div[2]/table/tbody/tr/td[5]/span/text()')
        return "“{}”当前牛客rating为：{}".format(name, rating[0])



if __name__ == '__main__':
    nc = NC()
    logger.info(nc.info)
    # pprint.pprint(asyncio.run(get_contest()))
    logger.debug(asyncio.run(nc.get_rating("ING__")))

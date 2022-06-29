from oj_api.global_pk import *


class LC(Contest):
    def __init__(self):
        self.HOST = "https://leetcode-cn.com/"
        self.PATH = {
            "contestList": "graphql"
        }
        self.HEADER = {
            "accept": "*/*",
            "accept-encoding": "gzip,deflate,br",
            "accept-language": "zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/json",
            # "cookie": response.cookies,
            "origin": "https://leetcode-cn.com",
            "pragma": "no-cache",
            "referer": "https://leetcode-cn.com/contest/",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            # 'x-csrftoken': response.cookies
        }
        super().__init__()

    async def get_contest(self):
        url_data = self.HOST + self.PATH["contestList"]
        payload = {
            "operationName": "null",
            "query": "{\n  contestUpcomingContests {\n    containsPremium\n    title\n    cardImg\n    titleSlug\n    description\n    startTime\n    duration\n    originStartTime\n    isVirtual\n    isLightCardFontColor\n    company {\n      watermark\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {}
        }
        json_data = httpx.post(url=url_data, json=payload, headers=self.HEADER).json()

        # print(json_data)

        res = []
        try:
            contest_info = json_data['data']['contestUpcomingContests']

            # print(type(contest_info))

            for contest in contest_info:
                html = etree.HTML(contest['description'])
                company = html.xpath("/html/body/div/div/div/p[1]/text()")[0]

                begin_time = contest['startTime']
                year = time.localtime(begin_time).tm_year
                mon = time.localtime(begin_time).tm_mon
                day = time.localtime(begin_time).tm_mday
                hour = time.localtime(begin_time).tm_hour
                minute = time.localtime(begin_time).tm_min
                second = time.localtime(begin_time).tm_sec

                contest_info = "比赛名称：{}\n" \
                               "赞助公司：{}\n" \
                               "开始时间：{}\n" \
                               "持续时间：{}\n" \
                               "比赛地址：{}".format(
                    contest['title'],
                    company,
                    "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, mon, day, hour, minute, second),
                    "{}小时{:02d}分钟".format(contest['duration'] // 3600, contest['duration'] % 3600 // 60),
                    "https://leetcode-cn.com/contest/" + contest['titleSlug'])

                res.append(
                    {
                        'contest_info': contest_info,
                        'begin_time': begin_time,
                        'during_time': contest['duration'],
                    }
                )

            # print(res)
            res.sort(key=lambda x: x['begin_time'], reverse=False)
            return res, res[0]['begin_time'], res[0]['during_time']
        except:
            return [
                       {
                           "contest_info": "最近没有比赛~",
                           'begin_time': NO_CONTEST,
                           'during_time': NO_CONTEST,
                       }
                   ], NO_CONTEST, NO_CONTEST

    # TODO 获取力扣分数
    async def get_rating(self, name):
        pass


if __name__ == '__main__':
    lc = LC()
    pprint.pprint(lc.list)

import pprint
import time

from oj_api.global_pk import *


# from global_pk import *

class ATC(Contest):
    def __init__(self):
        self.HOST = "https://atcoder.jp/"
        self.PATH = {
            "userRating": "users/",
            "contestList": "contests/"
        }
        super().__init__()

    async def get_contest(self):
        try:
            url = self.HOST + self.PATH["contestList"]

            # 获取网页到本地
            html = httpx.get(url).text
            # await(text_save('./atc_contest.html', html))

            # 转化为能处理的对象
            h5 = etree.fromstring(html, etree.HTMLParser())
            # result = etree.tostring(h5)

            count_xpath = "count(//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr)"
            # print(h5.xpath(count_xpath))
            count = h5.xpath(count_xpath)

            # 获取当前界面展示了多少比赛信息
            count = int(count)

            res = []

            for i in range(1, count + 1):
                # 构建对应的xpath
                time_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[{}]/td[1]/a/time/text()".format(
                    i)
                contest_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[{}]/td[2]/a/text()".format(
                    i)
                during_time_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[{}]/td[3]/text()".format(
                    i)
                contest_url_xpath = "//*[@id=\"contest-table-upcoming\"]/div/div/table/tbody/tr[{}]/td[2]/a/@href".format(
                    i)

                # 获取对应的信息
                contest_time = h5.xpath(time_xpath)[0]
                contest_name = h5.xpath(contest_xpath)[0]
                during_time = h5.xpath(during_time_xpath)[0].split(':')
                contest_url = h5.xpath(contest_url_xpath)[0]

                during_time_hour = during_time[0]
                during_time_min = during_time[1]

                # debug
                # pprint.pprint(contest_time)
                # pprint.pprint(contest_name)
                # pprint.pprint(during_time)
                # pprint.pprint(url + str(contest_url[1:]))

                # os.remove("./atc_contest.html")

                contest_info = "比赛名称：{}\n开始时间：{}\n持续时间：{}\n比赛地址：{}".format(
                    contest_name,
                    contest_time,
                    "{}小时{:02d}分钟".format(int(during_time_hour), int(during_time_min)),
                    "https://atcoder.jp/" + str(contest_url[1:])
                )

                # 转化为时间戳
                begin_time = int(time.mktime(
                    time.strptime(contest_time[:-5], "%Y-%m-%d %H:%M:%S"))) - 3600  # 默认是东京时间，减一为了转为北京时间
                during_time = int(during_time_hour) * 3600 + int(during_time_min) * 60

                res.append({
                    'contest_info': contest_info,
                    'begin_time': begin_time,
                    'during_time': during_time,
                })

            return res, res[0]['begin_time'], res[0]['during_time']
        except:
            # 如果请求失败就判断时候应当更换比赛信息
            return self.get_next_contest()

    async def get_rating(self, name):  # 返回一个列表，如果不存在用户则是空列表
        url = self.HOST + self.PATH["userRating"] + name

        # 获取网页
        html = httpx.get(url).text

        # 转化为能处理的对象
        # h5 = etree.parse("./atc_usr.html", etree.HTMLParser())
        # result = etree.tostring(h5)

        # 构建对应的xpath
        # rank_xpath = "/html/body/div[1]/div/div[1]/div[3]/table/tbody/tr[2]/td/span[0]"

        # 获取对应的属性值
        # rank = h5.xpath(rank_xpath)

        # -----xpath办法失败，不知道为什么获取的值都是空的，有没有懂的大佬可以解答一下qwq-------

        r = r'<th class="no-break">Rating<\/th><td><span class=(.*?)>(.*?)<\/span>'
        results = re.findall(r, html, re.S)
        try:
            return results[0][1]
        except:
            return -1


if __name__ == '__main__':
    # asyncio.run(get_contest_lately())
    atc = ATC()
    pprint.pprint(atc.list)
    # print(asyncio.run(get_usr_rank("432423")))
    pass

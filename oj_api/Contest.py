import abc
import asyncio
import time


class Contest(metaclass=abc.ABCMeta):
    def __init__(self):
        self.updated_time = time.time()
        self.info, self.begin_time, self.during_time = "", 0, 0  # 时间全以时间戳为单位
        self.info, self.begin_time, self.during_time = asyncio.run(self.get_contest())


    async def update_contest(self, flag=0):  # flag=1代表强制更新
        # 在要求强制更新或者超过上次跟新两个小时后或者上一场已经结束
        if int(time.time()) - self.updated_time >= 2 * 3600 or int(time.time()) >= self.begin_time + self.during_time or flag == 1:
            self.updated_time = int(time.time())
            self.info, self.begin_time, self.during_time = await self.get_contest()
            print("更新{}比赛成功".format(self.__class__.__name__))
        # return self.info

    def show_all(self):
        print("info : {}\nduring_time : {}\nbegin_time : {}\n update_time : {}".format(self.info, self.during_time, self.begin_time, self.updated_time))

    @abc.abstractmethod
    async def get_contest(self):
        pass

    @abc.abstractmethod
    async def get_rating(self, name):
        pass

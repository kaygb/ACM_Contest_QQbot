import os
import re
import sys
import time
import asyncio
import random
import httpx
import datetime
import mirai
from log import Log
from other_operation import random_qcjj
from oj_api import cf_api, atc_api, lc_api, nc_api, Contest
from mirai.models import NewFriendRequestEvent, BotInvitedJoinGroupRequestEvent
from mirai import Startup, Shutdown, MessageEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai_extensions.trigger import HandlerControl, Filter
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain, MessageChain, Image

sys.stdout = Log.Logger()  # 定义log类
sys.stderr = Log.Logger()
scheduler = AsyncIOScheduler()
API_KEY = 'SWeKQBWfoYiQFuZSJ'

cf = cf_api.CF()

atc = atc_api.ATC()

nc = nc_api.NC()

lc = lc_api.LC()

print(cf.info)
print(atc.info)
print(nc.info)
print(lc.info)

# 读取本地保存的要通知的人和群号，没有自动创建
if not os.path.exists('friend.txt'):
    f = open('friend.txt', 'w')
    f.write('')
    f.close()

if not os.path.exists('group.txt'):
    f = open('group.txt', 'w')
    f.write('')
    f.close()

f = open('friend.txt', 'r')
FRIENDS = set(map(lambda x: x.strip(), f.readlines()))
f.close()
f = open('group.txt', 'r')
GROUPS = set(map(lambda x: x.strip(), f.readlines()))
f.close()


async def query_now_weather(city: str) -> str:
    """查询天气数据。"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f'https://api.seniverse.com/v3/weather/now.json', params={
                'key': API_KEY,
                'location': city,
                'language': 'zh-Hans',
                'unit': 'c',
            })
            time.sleep(0.5)
            resp.raise_for_status()
            data = resp.json()
            return f'当前{data["results"][0]["location"]["name"]}天气为' \
                   f'{data["results"][0]["now"]["text"]}，' \
                   f'气温{data["results"][0]["now"]["temperature"]}℃。'
        except (httpx.NetworkError, httpx.HTTPStatusError, KeyError):
            return f'抱歉，没有找到{city}的天气数据。'


async def query_today_contest():
    global cf, atc, nc, lc

    res = ""

    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day

    print(cf.info)
    print(lc.info)
    print(atc.info)
    print(nc.info)
    print(lc.info)

    # CF
    if time.localtime(cf.begin_time).tm_mon == mon and time.localtime(
            cf.begin_time).tm_mday == day:
        print(1)
        res += (cf.info + '\n\n')

    # ATC
    if time.localtime(atc.begin_time).tm_mon == mon and time.localtime(
            atc.begin_time).tm_mday == day:
        print(2)
        res += (atc.info + '\n\n')

    # NC
    if time.localtime(nc.begin_time).tm_mon == mon and time.localtime(
            nc.begin_time).tm_mday == day:
        print(3)
        res += (nc.info + '\n\n')

    # LC
    if time.localtime(lc.begin_time).tm_mon == mon and time.localtime(
            lc.begin_time).tm_mday == day:
        print(4)
        res += (lc.info + '\n\n')

    print(res)

    return res


async def query_next_contest():
    global cf, atc, nc, lc
    # 看看需不需要更新
    await cf.update_contest()
    await atc.update_contest()
    await nc.update_contest()
    await lc.update_contest()

    next_contest = [[cf.info, cf.begin_time], [atc.info, atc.begin_time], [nc.info, nc.begin_time],
                    [lc.info, lc.begin_time]]
    next_contest.sort(key=lambda x: x[1])
    return next_contest


if __name__ == '__main__':
    bot = Mirai(
        qq=3409201437,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='yirimirai', host='localhost', port=8080
        )
    )
    hdc = HandlerControl(bot)  # 事件接收器


    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器


    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器


    @bot.on(NewFriendRequestEvent)
    async def allow_request_friend(event: NewFriendRequestEvent):  # 有新用户好友申请就自动通过
        await bot.allow(event)


    @bot.on(BotInvitedJoinGroupRequestEvent)
    async def allow_request_invite_group(event: BotInvitedJoinGroupRequestEvent):  # 被邀请进群自动通过
        await bot.allow(event)


    @bot.on(MessageEvent)
    async def on_friend_message(event: MessageEvent):
        if str(event.message_chain) == '你好':
            await bot.send(event, 'Hello, World!')


    @bot.on(MessageEvent)
    async def show_list(event: MessageEvent):  # 功能列表展示
        msg = "".join(map(str, event.message_chain[Plain]))

        menu = "\n查询天气 城市 -> 查询市级城市实时天气" \
               "\n查询cf分数 id -> 查询对应id的 cf 分数" \
               "\ncf -> 近场 cf 比赛" \
               "\n随机cf -> 随机cf round" \
               "\n今日随机cf -> 每天的随机cf round" \
               "\natc -> 最新的AtCoder比赛" \
               "\n牛客 -> 最新的牛客比赛" \
               "\nlc -> 最新的力扣比赛" \
               "\ntoday -> 查询今天比赛" \
               "\nnext -> 查询下一场比赛" \
               "\n来只清楚 -> 随机qcjj" \
               "\nsetu/涩图 -> 涩图" \
               "\n添加通知 -> 每天早上会为你发送当日比赛信息哦qwq" \
               "\n删除通知 -> 就是不再提醒你了" \
               "\nbug联系 -> 1095490883" \
               "\n项目地址 -> 获取项目地址"

        if msg == ".help":
            if isinstance(event, GroupMessage):
                await bot.send(event, [At(event.sender.id), menu])
            else:
                await bot.send(event, [menu])


    # CF

    @bot.on(MessageEvent)
    async def query_cf_rank(event: MessageEvent):  # 查询对应人的分数
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'^查询CF分数\s*([\w.-]+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询cf分数\s*([\w.-]+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的CF分数$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的cf分数$', msg.strip())

        if m:
            name = m.group(1)
            # print(name)

            global cf
            if int(time.time()) - cf.updated_time < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(cf.updated_time + 5 - int(time.time())))
                return

            # await bot.send(event, '查询中……')
            statue = await cf.get_rating(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    @bot.on(MessageEvent)
    async def query_cf_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'cf', msg.strip())
        #
        # if m is None:
        #     m = re.match(r'CF', msg.strip())

        if msg.strip().lower() == 'cf':
            global cf

            print("查询cf比赛")

            if int(time.time()) - cf.updated_time < 5:
                await bot.send(event, cf.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await cf.update_contest()
            await bot.send(event, cf.info)


    @bot.on(MessageEvent)
    async def get_random_cf_contest(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip().lower() == '随机cf':
            global cf
            print("随机cf")
            await bot.send(event, await cf.get_random_contest())


    @bot.on(MessageEvent)
    async def get_daily_random_cf_contest(event: MessageEvent, _hack=[None, None]):
        msg = "".join(map(str, event.message_chain[Plain])).strip().lower()

        if msg == "今日随机cf" or msg == "更新今日随机cf":
            print("今日随机cf")
            if not _hack[0] or _hack[0] != datetime.date.today() or msg == "更新今日随机cf":
                _hack[0] = datetime.date.today()
                global cf
                _hack[1] = await cf.get_random_contest()
            await bot.send(event, _hack[1])


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(cf.begin_time - 15 * 60).tm_mon,
                                         day=time.localtime(cf.begin_time - 15 * 60).tm_mday,
                                         hour=time.localtime(cf.begin_time - 15 * 60).tm_hour,
                                         minute=time.localtime(cf.begin_time - 15 * 60).tm_min,
                                         timezone='Asia/Shanghai'))
    async def cf_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_cf.jpg')
        ])
        for friend in FRIENDS:
            try:
                await bot.send_friend_message(friend, message_chain)  # 发送个人
            except:
                print("不存在qq号为 {} 的好友".format(friend))

        for group in GROUPS:
            try:
                await bot.send_group_message(group, message_chain)  # 发送群组
            except:
                print("不存在群号为 {} 的群组".format(group))
        # await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    @scheduler.scheduled_job(
        CronTrigger(month=time.localtime(cf.begin_time + cf.during_time).tm_mon,
                    day=time.localtime(cf.begin_time + cf.during_time).tm_mday,
                    hour=time.localtime(cf.begin_time + cf.during_time).tm_hour,
                    minute=time.localtime(cf.begin_time + cf.during_time).tm_min,
                    timezone='Asia/Shanghai'))
    async def cf_xia_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/down_cf.jpg')
        ])
        for friend in FRIENDS:
            try:
                await bot.send_friend_message(friend, message_chain)  # 发送个人
            except:
                print("不存在qq号为 {} 的好友".format(friend))

        for group in GROUPS:
            try:
                await bot.send_group_message(group, message_chain)  # 发送群组
            except:
                print("不存在群号为 {} 的群组".format(group))
        # await bot.send_group_message(763537993, message_chain)  # 874149706测试号

        global cf  # 比完接着更新
        await cf.update_contest()


    # ATC
    @bot.on(MessageEvent)
    async def query_atc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'atc', msg.strip())

        # if m is None:
        #     m = re.match(r'ATC', msg.strip())

        if msg.strip().lower() == 'atc':
            global atc

            print("查询atc比赛")

            if int(time.time()) - atc.updated_time < 5:
                await bot.send(event, atc.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)

            await atc.update_contest()
            await bot.send(event, atc.info)


    @bot.on(MessageEvent)
    async def query_atc_rank(event: MessageEvent):  # 查询对应人的分数
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'^查询ATC分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询atc分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的atc分数$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的ATC分数$', msg.strip())

        if m:
            name = m.group(1)
            # print(name)

            global atc
            if int(time.time()) - atc.updated_time < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(atc.updated_time + 5 - int(time.time())))
                return

            # await bot.send(event, '查询中……')
            statue = await atc.get_rating(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    # nowcoder

    @bot.on(MessageEvent)
    async def query_nc_rating(event: MessageEvent):  # 查询牛客rating
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^查询牛客分数\s*([\u4e00-\u9fa5\w.-]+)\s*$', msg.strip())
        if m:
            uname = m.group(1)
            rating = await nc.get_rating(uname)
            await bot.send(event, rating)


    @bot.on(MessageEvent)
    async def query_nc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'牛客', msg.strip())

        if msg.strip() == "牛客" or msg.strip() == 'nc':
            global nc

            print("查询牛客比赛")

            if int(time.time()) - nc.updated_time < 5:
                await bot.send(event, nc.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await nc.update_contest()
            await bot.send(event, nc.info if nc.info != -1 else "获取比赛时出错，请联系管理员")


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(nc.begin_time - 10 * 60).tm_mon,
                                         day=time.localtime(nc.begin_time - 10 * 60).tm_mday,
                                         hour=time.localtime(nc.begin_time - 10 * 60).tm_hour,
                                         minute=time.localtime(nc.begin_time - 10 * 60).tm_min,
                                         timezone='Asia/Shanghai'))
    async def nc_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_nc.png')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    # 力扣
    @bot.on(MessageEvent)
    async def query_lc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'lc', msg.strip())

        if msg == "lc":
            print("查询力扣比赛")

            global lc

            if int(time.time()) - lc.updated_time < 5:
                await bot.send(event, lc.info if lc.info != -1 else "获取比赛时出错，请联系管理员")
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await lc.update_contest()
            await bot.send(event, lc.info if lc.info != -1 else "获取比赛时出错，请联系管理员")


    # other
    @bot.on(MessageEvent)
    async def query_today(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg == 'today':
            res = await query_today_contest()

            if res != '':
                await bot.send(event, "为您查询到今日的比赛有：\n\n" + res.strip())
            else:
                await bot.send(event, "今日无比赛哦~")


    @bot.on(MessageEvent)
    async def qcjj_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'来只清楚', msg.strip())
        if msg == '来只清楚':
            print("来只清楚")
            img_list = os.listdir('./pic/qcjj/')
            img_local = './pic/qcjj/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)


    @bot.on(MessageEvent)
    async def echo(event: MessageEvent):  # 复读机
        msg = "".join(map(str, event.message_chain[Plain])).strip()
        m = re.match(r'^echo\s*(\w+)\s*$', msg)
        if m and At(bot.qq) in event.message_chain:
            await bot.send(event, msg)


    @bot.on(MessageEvent)
    async def on_group_message(event: MessageEvent):  # 返回
        if At(bot.qq) in event.message_chain and len("".join(map(str, event.message_chain[Plain]))) == 0:
            await bot.send(event, [At(event.sender.id), '你在叫我吗？'])


    @bot.on(MessageEvent)
    async def weather_query(event: MessageEvent):  # 天气查询
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^查询天气\s*(\w+)\s*$', msg.strip())
        if m:
            print("cha xun")
            # 取出指令中的地名
            city = m.group(1)
            print(city)
            # await bot.send(event, '查询中……')
            # 发送天气消息
            await bot.send(event, await query_now_weather(city))


    @bot.on(MessageEvent)
    async def project_address(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg == '项目地址':
            await bot.send(event, "大佬可以点个star✨吗qwq\nhttps://github.com/INGg/ACM_Contest_QQbot")


    # setu
    @bot.on(MessageEvent)
    async def setu_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'setu', msg.strip())
        # if m is None:
        # m = re.match(r'涩图', msg.strip())
        if msg.strip() == 'setu' or msg.strip() == '涩图':
            print("setu")
            img_list = os.listdir('./pic/setu/')
            img_local = './pic/setu/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)


    # color_img
    @bot.on(MessageEvent)
    async def color_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'色图', msg.strip())
        if msg.strip() == '色图':
            print("色图")
            message_chain = MessageChain([
                await Image.from_local('./pic/color.jpg')
            ])
            await bot.send(event, message_chain)


    @bot.on(MessageEvent)
    async def yxc_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'管哥哥', msg.strip())
        if msg.strip().lower() == '来只yxc':
            print("yxc")
            img_list = os.listdir('./pic/yxc/')
            img_local = './pic/yxc/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)


    @bot.on(MessageEvent)
    async def ggg_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'管哥哥', msg.strip())
        if msg.strip() == '管哥哥':
            print("ggg")
            img_list = os.listdir('./pic/ggg/')
            img_local = './pic/ggg/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)


    # daily
    @scheduler.scheduled_job('interval', hours=2, timezone='Asia/Shanghai')
    async def update_contest_info():
        async def update(oj):
            while True:
                await oj.update_contest(flag=1)
                if oj.info != -1:
                    await asyncio.sleep(5)  # 休息5s
                    break

        now = time.localtime()
        print()
        print(time.strftime("%Y-%m-%d", now))  # 给log换行

        global cf
        await update(cf)

        global atc
        await update(atc)

        global nc
        await update(nc)

        global lc
        await update(nc)


    @bot.on(MessageEvent)
    async def next_contest(event: MessageEvent):  # 查询近期比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip().lower() == 'next':
            contest = await query_next_contest()
            if contest[0][1] != 0:
                res = '找到最近的 1 场比赛如下：\n\n' + contest[0][0]
                await bot.send(event, res)
            else:
                await bot.send(event, '最近没有比赛哦~')


    @bot.on(MessageEvent)
    async def add_notify(event: MessageEvent):  # 添加通知列表
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip() == '添加通知':
            try:
                if isinstance(event, GroupMessage):
                    group_id = event.sender.group.id
                    global GROUPS

                    if str(group_id) not in GROUPS:
                        f = open('group.txt', 'a')
                        f.write("{}\n".format(group_id))
                        GROUPS.add(str(group_id))
                        f.close()
                        print("添加群通知：{}".format(group_id))
                        await bot.send(event, '添加成功~')
                    else:
                        await bot.send(event, '已经添加过啦~')
                else:
                    qq_id = event.sender.id
                    global FRIENDS
                    if str(qq_id) not in FRIENDS:
                        f = open('friend.txt', 'a')
                        f.write("{}\n".format(qq_id))
                        FRIENDS.add(str(qq_id))
                        f.close()
                        print("添加个人通知：{}".format(qq_id))
                        await bot.send(event, '添加成功~')
                    else:
                        await bot.send(event, '已经添加过啦~')
            except:
                await bot.send(event, '添加失败')


    @bot.on(MessageEvent)
    async def del_notify(event: MessageEvent):  # 删除通知列表
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip() == '删除通知':
            await bot.send(event, '删除通知还没想好怎么写qwq，请联系管理员删除哦~ qq：1095490883')


    @scheduler.scheduled_job(CronTrigger(hour=7, minute=30), timezone='Asia/Shanghai')
    async def notify_contest_info():
        res = await query_today_contest()

        # friends = ['1095490883', '942845546', '2442530380', '601621184']
        # groups = ['687601411', '763537993']

        if res != '':
            # 发送当日信息
            msg = "今日的比赛有：\n\n" + res.strip()
            for friend in FRIENDS:
                try:
                    await bot.send_friend_message(friend, msg)  # 发送个人
                except:
                    print("不存在qq号为 {} 的好友".format(friend))

            for group in GROUPS:
                try:
                    await bot.send_group_message(group, msg)  # 发送群组
                except:
                    print("不存在群号为 {} 的群组".format(group))


    # debug
    @Filter(FriendMessage)
    def filter_(event: FriendMessage):  # 定义过滤器，在过滤器中对事件进行过滤和解析
        global cf, atc, lc, nc
        msg = str(event.message_chain)
        # 如果好友发送的消息格式正确，过滤器返回消息的剩余部分。比如，好友发送“ / command”，过滤器返回'command'。
        # 如果好友发送的消息格式不正确，过滤器隐式地返回None。
        if msg.startswith('\\'):
            return msg[1:]


    @hdc.on(filter_)
    async def handler(event: FriendMessage, payload: str):
        global cf
        # cf.begin_time = int(time.time())
        # cf.during_time = 60
        if payload == "cf":
            await cf.update_contest(flag=1)
        if payload == 'friend':
            await bot.send(event, str(FRIENDS))
        if payload == 'group':
            await bot.send(event, str(GROUPS))
        await bot.send(event, f'命令 {payload} 执行成功。')


    bot.run()

import os
import re
import sys
import time
import json
import httpx
import mirai
import random
import asyncio
import datetime
from log import Log
from other_operation import qfnu_daka
from mirai import Startup, Shutdown, MessageEvent
from apscheduler.triggers.cron import CronTrigger
from mirai.models.api import MessageFromIdResponse
from mirai_extensions.trigger import HandlerControl, Filter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from oj_api import cf_api, atc_api, lc_api, nc_api
from mirai.models import NewFriendRequestEvent, BotInvitedJoinGroupRequestEvent, Quote
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain, MessageChain, Image

sys.stdout = Log.Logger()  # 定义log类
sys.stderr = Log.Logger()
scheduler = AsyncIOScheduler()
API_KEY = 'SWeKQBWfoYiQFuZSJ'

cf = cf_api.CF()

atc = atc_api.ATC()

nc = nc_api.NC()

lc = lc_api.LC()

print(cf.list)
print(atc.list)
print(nc.list)
print(lc.list)

# 读取本地保存的要通知的人和群号，没有自动创建
if not os.path.exists('noti.json'):
    with open('noti.json', 'w') as f:
        json.dump({'Friends': [], 'Groups': []}, f)

# 随机发送图片的准备工作
pic_qcjj = os.listdir('./pic/qcjj/')
pic_setu = os.listdir('./pic/setu/')


# 保证不随机一遍之后不会出现重复的
async def lzqc():
    global pic_qcjj
    while True:
        if pic_qcjj:
            pic_name = random.choice(pic_qcjj)
            img_local = './pic/qcjj/' + pic_name
            pic_qcjj.remove(pic_name)
            return img_local
        else:
            pic_qcjj = os.listdir('./pic/qcjj/')


async def lz_setu():
    global pic_setu
    while True:
        if pic_setu:
            pic_name = random.choice(pic_setu)
            img_local = './pic/setu/' + pic_name
            pic_setu.remove(pic_name)
            return img_local
        else:
            pic_setu = os.listdir('./pic/setu/')


# 添加定时器
async def sche_add(func, implement, id=None):
    scheduler.add_job(func, CronTrigger(month=time.localtime(implement).tm_mon,
                                        day=time.localtime(implement).tm_mday,
                                        hour=time.localtime(implement).tm_hour,
                                        minute=time.localtime(
                                            implement).tm_min,
                                        second=time.localtime(
                                            implement).tm_sec,
                                        timezone='Asia/Shanghai'), id=id, misfire_grace_time=60)


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

    print(cf.list)
    print(lc.list)
    print(atc.list)
    print(nc.list)
    print(lc.list)

    # CF
    if time.localtime(cf.begin_time).tm_mon == mon and time.localtime(
            cf.begin_time).tm_mday == day:
        print(1)
        res += (cf.list[0]['contest_info'] + '\n\n')

    # ATC
    if time.localtime(atc.begin_time).tm_mon == mon and time.localtime(
            atc.begin_time).tm_mday == day:
        print(2)
        res += (atc.list[0]['contest_info'] + '\n\n')

    # NC
    if time.localtime(nc.begin_time).tm_mon == mon and time.localtime(
            nc.begin_time).tm_mday == day:
        print(3)
        res += (nc.list[0]['contest_info'] + '\n\n')

    # LC
    if time.localtime(lc.begin_time).tm_mon == mon and time.localtime(
            lc.begin_time).tm_mday == day:
        print(4)
        res += (lc.list[0]['contest_info'] + '\n\n')

    print(res)

    return res


async def query_next_contest():
    global cf, atc, nc, lc
    # 看看需不需要更新
    await cf.update_contest()
    await atc.update_contest()
    await nc.update_contest()
    await lc.update_contest()

    next_contest = [[cf.list[0]['contest_info'], cf.begin_time], [atc.list[0]['contest_info'], atc.begin_time], [nc.list[0]['contest_info'], nc.begin_time],
                    [lc.list[0]['contest_info'], lc.begin_time]]
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
    # 被邀请进群自动通过
    async def allow_request_invite_group(event: BotInvitedJoinGroupRequestEvent):
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
               "\n随机cf -> 随机cf round（随机近180天到3年内的vp）" \
               "\n随机edu/div1234 -> 随机固定场次" \
               "\n今日随机cf -> 每天的随机cf round" \
               "\natc -> 最新的AtCoder比赛" \
               "\n牛客/nc -> 最新的牛客比赛" \
               "\nlc -> 最新的力扣比赛" \
               "\ntoday -> 查询今天比赛" \
               "\nnext -> 查询下一场比赛" \
               "\n来只清楚 -> 随机qcjj" \
               "\n添加清楚/叉姐->使用qq回复功能选择图片保存到图库" \
               "\n来只yxc -> 随机yxc" \
               "\nsetu/涩图 -> 涩图" \
               "\n开启通知 -> 每天早上会为你发送当日比赛信息哦qwq" \
               "\n关闭通知 -> 就是不再提醒你了" \
               "\nbug联系 -> 1095490883" \
               "\n项目地址 -> 获取项目地址" \
               "\nps:所有的功能私聊均可用哦，加好友自动通过申请，然后可以邀请到自己的群里哦~"

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
            print("查询cf" + name)

            global cf
            if int(time.time()) - cf.updated_time < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(int(cf.updated_time + 5 - int(time.time()))))
                return

            # await bot.send(event, '查询中……')
            cf.updated_time = time.time()
            statue = await cf.get_rating(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")

    @bot.on(MessageEvent)
    async def query_cf_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip().lower() == 'cf':
            global cf

            print("查询cf比赛")

            info = ""
            for i in range(min(3, len(cf.list))):
                info += cf.list[i]['contest_info'] + '\n'

            if int(time.time()) - cf.updated_time < 5:
                await bot.send(event, "找到最近的{}场的Codeforces比赛为：\n".format(min(3, len(cf.list))) + info)
                return

            await cf.update_contest()

            info = ""
            for i in range(min(3, len(cf.list))):
                info += cf.list[i]['contest_info'] + '\n'

            await bot.send(event, "找到最近的{}场的Codeforces比赛为：\n".format(min(3, len(cf.list))) + info)

    @bot.on(MessageEvent)
    async def get_random_cf_contest(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        global cf
        if msg.strip().lower() == '随机cf':
            print("随机cf")
            await bot.send(event, await cf.get_random_contest('normal'))
        if msg.strip().lower() == '随机edu':
            print("随机edu")
            await bot.send(event, await cf.get_random_contest('edu'))
        if msg.strip().lower() == '随机div1':
            print("随机div1")
            await bot.send(event, await cf.get_random_contest('div1'))
        if msg.strip().lower() == '随机div2':
            print("随机div2")
            await bot.send(event, await cf.get_random_contest('div2'))
        if msg.strip().lower() == '随机div3':
            print("随机div3")
            await bot.send(event, await cf.get_random_contest('div3'))
        if msg.strip().lower() == '随机div4':
            print("随机div4")
            await bot.send(event, await cf.get_random_contest('div4'))

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

    async def cf_shang_hao():
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()

        message_chain = MessageChain([
            await Image.from_local('pic/up_cf.jpg')
        ])
        for friend in Friends:
            try:
                await asyncio.sleep(0.2)  # 减缓发送速度，降低疯狂的可能性
                await bot.send_friend_message(friend, message_chain)  # 发送个人
            except:
                print("不存在qq号为 {} 的好友".format(friend))

        for group in Groups:
            try:
                await asyncio.sleep(0.2)
                await bot.send_group_message(group, message_chain)  # 发送群组
            except:
                print("不存在群号为 {} 的群组".format(group))

    async def cf_xia_hao():
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()

        message_chain = MessageChain([
            await Image.from_local('pic/down_cf.jpg')
        ])
        for friend in Friends:
            try:
                await asyncio.sleep(0.2)
                await bot.send_friend_message(friend, message_chain)  # 发送个人
            except:
                print("不存在qq号为 {} 的好友".format(friend))

        for group in Groups:
            try:
                await asyncio.sleep(0.2)
                await bot.send_group_message(group, message_chain)  # 发送群组
            except:
                print("不存在群号为 {} 的群组".format(group))

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

            info = ""
            for i in range(min(3, len(atc.list))):
                info += atc.list[i]['contest_info'] + '\n'

            if int(time.time()) - atc.updated_time < 5:
                await bot.send(event, "找到最近的{}场的AtCoder比赛为：\n".format(min(3, len(atc.list))) + info)
                return

            info = ""
            for i in range(min(3, len(atc.list))):
                info += atc.list[i]['contest_info'] + '\n'

            await atc.update_contest()
            await bot.send(event, "找到最近的{}场的AtCoder比赛为：\n".format(min(3, len(atc.list))) + info)

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
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(int(atc.updated_time + 5 - int(time.time()))))
                return

            # await bot.send(event, '查询中……')
            atc.updated_time = time.time()
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

            info = ""
            for i in range(min(3, len(nc.list))):
                info += nc.list[i]['contest_info'] + '\n'

            if int(time.time()) - nc.updated_time < 5:
                await bot.send(event, "找到最近的{}场的牛客比赛为：\n".format(min(3, len(nc.list))) + info)
                return

            info = ""
            for i in range(min(3, len(nc.list))):
                info += nc.list[i]['contest_info'] + '\n'

            await nc.update_contest()
            await bot.send(event, "找到最近的{}场的牛客比赛为：\n".format(min(3, len(nc.list))) + info)

    async def nc_shang_hao():
        with open('noti.json', 'r') as f:
            _, GROUPS = json.load(f).values()
        message_chain = MessageChain([
            await Image.from_local('pic/up_nc.png')
        ])
        for group in GROUPS:
            try:
                await asyncio.sleep(0.2)
                await bot.send_group_message(group, message_chain)  # 发送群组
            except:
                print("不存在群号为 {} 的群组".format(group))

    # 力扣

    @bot.on(MessageEvent)
    async def query_lc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'lc', msg.strip())

        if msg == "lc":
            print("查询力扣比赛")

            global lc

            info = ""
            for i in range(min(3, len(lc.list))):
                info += lc.list[i]['contest_info'] + '\n'

            if int(time.time()) - lc.updated_time < 5:
                await bot.send(event, "找到最近的{}场的力扣比赛为：\n".format(min(3, len(lc.list))) + info)
                return

            info = ""
            for i in range(min(3, len(lc.list))):
                info += lc.list[i]['contest_info'] + '\n'

            await lc.update_contest()
            await bot.send(event, "找到最近的{}场的力扣比赛为：\n".format(min(3, len(lc.list))) + info)

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
    async def echo(event: MessageEvent):  # 复读机
        msg = "".join(map(str, event.message_chain[Plain])).strip()
        m = re.match(r'^echo\s*(\w+)\s*$', msg)
        if m and At(bot.qq) in event.message_chain:
            await bot.send(event, msg)

    @bot.on(MessageEvent)
    async def on_group_message(event: MessageEvent):  # 返回
        if At(bot.qq) in event.message_chain and len("".join(map(str, event.message_chain[Plain]))) in [0, 1]:
            message_chain = MessageChain([
                await Image.from_local('./pic/at_bot.gif')
            ])
            await bot.send(event, message_chain)

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

    # 回复项目地址

    @bot.on(MessageEvent)
    async def project_address(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg == '项目地址':
            await bot.send(event, "大佬可以点个star✨吗qwq\nhttps://github.com/INGg/ACM_Contest_QQbot")

    # 随机图片功能

    @bot.on(MessageEvent)
    async def add_image(event: MessageEvent):
        global pic_qcjj
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg.strip() == '添加清楚':
            if event.sender.group.id in [601621184, 839594887, 874149706, 215516112]:
                quotes = event.message_chain[Quote]
                for quote in quotes:
                    message: MessageFromIdResponse = await bot.message_from_id(quote.id)
                    images = message.data.message_chain[Image]
                    for image in images:
                        all_img_qcjj = os.listdir('./pic/qcjj/')
                        suffix = image.image_id.split('.')[1]
                        id_qcjj = str(len(all_img_qcjj) + 1) + '.' + suffix
                        filename_qcjj = './pic/qcjj/' + id_qcjj
                        await image.download(filename_qcjj, None, False)
                        pic_qcjj.append(id_qcjj)
                        print("添加清楚成功")
                        await bot.send(event, '添加成功！')
            else:
                await bot.send(event, "本群暂无权限，请联系管理员！")

    @bot.on(MessageEvent)
    async def qcjj_query(event: MessageEvent):  # 来只清楚
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        if re.match(r'来只清楚', msg.strip()):
            print("来只清楚")
            img_local = await lzqc()
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # setu

    @bot.on(MessageEvent)
    async def setu_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'setu', msg.strip())
        if m is None:
            m = re.match(r'涩图', msg.strip())
        if m:
            print("setu")
            img_local = await lz_setu()
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

    # 来只yxc

    @bot.on(MessageEvent)
    async def yxc_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        if msg.strip().lower() == '来只yxc':
            print("yxc")
            img_list = os.listdir('./pic/yxc/')
            img_local = './pic/yxc/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # 来只gtg（提高二群功能）

    @bot.on(MessageEvent)
    async def gtg_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        # m = re.match(r'管哥哥', msg.strip())
        if msg.strip().lower() == '来只gtg':
            print("gtg")
            img_list = os.listdir('./pic/gtg/')
            img_local = './pic/gtg/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # 来只bs（提高二群功能）

    @bot.on(MessageEvent)
    async def bs_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'来只bs', msg.strip().lower())
        if m:
            print("bs")
            img_list = os.listdir('./pic/bs/')
            img_local = './pic/bs/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    @bot.on(MessageEvent)
    async def add_image(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg.strip() == '添加bs':
            if event.sender.group.id in [601621184, 839594887, 874149706, 215516112]:
                quotes = event.message_chain[Quote]
                for quote in quotes:
                    message: MessageFromIdResponse = await bot.message_from_id(quote.id)
                    images = message.data.message_chain[Image]
                    for image in images:
                        all_img_bs = os.listdir('./pic/bs/')
                        suffix = image.image_id.split('.')[1]
                        id_bs = str(len(all_img_bs) + 1) + '.' + suffix
                        filename_bs = './pic/bs/' + id_bs
                        await image.download(filename_bs, None, False)
                        print("添加bs成功")
                        await bot.send(event, '添加成功！')
            else:
                await bot.send(event, "本群暂无权限，请联系管理员！")

    # 来只叉姐

    @bot.on(MessageEvent)
    async def x_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'来只叉姐', msg.strip().lower())
        if m:
            print("x")
            img_list = os.listdir('./pic/x/')
            img_local = './pic/x/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # 添加叉姐
    @bot.on(MessageEvent)
    async def add_image(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg.strip() == '添加叉姐':
            if event.sender.group.id in [601621184, 839594887, 874149706, 215516112]:
                quotes = event.message_chain[Quote]
                for quote in quotes:
                    message: MessageFromIdResponse = await bot.message_from_id(quote.id)
                    images = message.data.message_chain[Image]
                    for image in images:
                        all_img_x = os.listdir('./pic/x/')
                        suffix = image.image_id.split('.')[1]
                        id_x = str(len(all_img_x) + 1) + '.' + suffix
                        filename_x = './pic/x/' + id_x
                        await image.download(filename_x, None, False)
                        print("添加叉姐成功")
                        await bot.send(event, '添加成功！')
            else:
                await bot.send(event, "本群暂无权限，请联系管理员！")

    # 来只管哥哥（限于qfnu功能）

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

    @bot.on(MessageEvent)
    async def qfnu(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg.strip() == 'dk':
            print('dk')
            info_list = qfnu_daka.dk()
            res = ""
            for info in info_list:
                print(info)
                res += info + '\n'
            await bot.send(event, res)

    # daily

    async def update_contest_info():
        async def update(oj):
            await oj.update_contest(flag=1)

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
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()

        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip() == '开启通知':
            try:
                if isinstance(event, GroupMessage):
                    group_id = event.sender.group.id
                    if str(group_id) not in Groups:
                        Groups.append(str(group_id))
                        print("添加群通知：{}".format(group_id))
                        await bot.send(event, '开启成功，来和我一起每天一百道题吧~')
                    else:
                        await bot.send(event, '已经开启过啦~米娜真是太积极了(*/ω＼*)')
                else:
                    qq_id = event.sender.id
                    if str(qq_id) not in Friends:
                        Friends.append(str(qq_id))
                        print("添加个人通知：{}".format(qq_id))
                        await bot.send(event, '开启成功，来和我一起每天一百道题吧~')
                    else:
                        await bot.send(event, '已经开启过啦~认真刷题的孩子有黑红名上~')
            except:
                await bot.send(event, '开启通知失败இ௰இ')

        with open('noti.json', 'w') as f:
            json.dump({"Friends": Friends, "Groups": Groups}, f)

    @bot.on(MessageEvent)
    async def del_notify(event: MessageEvent):  # 删除通知列表
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()

        msg = "".join(map(str, event.message_chain[Plain]))

        if msg.strip() == '关闭通知':
            try:
                if isinstance(event, GroupMessage):
                    group_id = event.sender.group.id
                    if str(group_id) in Groups:
                        Groups.remove(str(group_id))
                        print("删除群通知：{}".format(group_id))
                        await bot.send(event, '关闭成功QwQ，没有我的陪伴米娜也要好好刷题哦o(TヘTo)')
                    else:
                        await bot.send(event, '我还没push你们呢，你们就想赶我走,,ԾㅂԾ,,')
                else:
                    qq_id = event.sender.id
                    if str(qq_id) in Friends:
                        Friends.remove(str(qq_id))
                        print("删除通知：{}".format(qq_id))
                        await bot.send(event, '关闭成功QwQ，没有我的陪伴也要好好刷题哦o(TヘTo)')
                    else:
                        await bot.send(event, '我还没push你呢，你就想赶我走,,ԾㅂԾ,,')
            except:
                await bot.send(event, '删除失败！你们已经逃不出我的手掌心啦哼哼哼(￣y▽,￣)╭ ')

        with open('noti.json', 'w') as f:
            json.dump({"Friends": Friends, "Groups": Groups}, f)

    async def notify_contest_info():
        res = await query_today_contest()
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()
        # friends = ['1095490883', '942845546', '2442530380', '601621184']
        # groups = ['687601411', '763537993']

        if res != '':
            # 发送当日信息
            msg = "早上好呀！今日的比赛有：\n\n" + res.strip()
            for friend in Friends:
                try:
                    await asyncio.sleep(0.2)
                    await bot.send_friend_message(friend, msg)  # 发送个人
                except:
                    print("不存在qq号为 {} 的好友".format(friend))

            for group in Groups:
                try:
                    await asyncio.sleep(0.2)
                    await bot.send_group_message(group, msg)  # 发送群组
                except:
                    print("不存在群号为 {} 的群组".format(group))

    async def daily_qfnu_daka():
        info_list = qfnu_daka.dk()
        res = ""
        for info in info_list:
            print(info)
            res += info + '\n'
        print("daily_qfnu_daka")
        await bot.send_friend_message('1095490883', res)

    @scheduler.scheduled_job('interval', minutes=30, timezone='Asia/Shanghai')
    async def refresh_job():
        scheduler.remove_all_jobs()
        await update_contest_info()
        await sche_job()
        msg = 'success：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        await bot.send_friend_message(1095490883, msg)

    async def sche_job():
        global cf, atc, nc, lc
        # 每九个小时更新一下比赛信息
        scheduler.add_job(update_contest_info, 'interval', hours=9,
                          timezone='Asia/Shanghai', misfire_grace_time=60)
        # 每天早上七点半通知
        scheduler.add_job(notify_contest_info, CronTrigger(hour=7, minute=30, timezone='Asia/Shanghai'),
                          misfire_grace_time=60)
        # 重新启动刷新函数
        scheduler.add_job(refresh_job, 'cron', hour=5, minute=0, second=0, timezone='Asia/Shanghai',
                          misfire_grace_time=60)
        # 启动所有的定时任务
        scheduler.add_job(daily_qfnu_daka, CronTrigger(hour=8, timezone='Asia/Shanghai'),
                          misfire_grace_time=60)
        await sche_add(cf_shang_hao, cf.get_note_time())
        await sche_add(cf_xia_hao, cf.get_end_time())
        await sche_add(nc_shang_hao, nc.get_note_time())

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
        with open('noti.json', 'r') as f:
            Friends, Groups = json.load(f).values()
        global cf
        # cf.begin_time = int(time.time())
        # cf.during_time = 60
        if payload == "cf":
            await cf.update_contest(flag=1)
        if payload == 'friend':
            await bot.send(event, str(Friends))
        if payload == 'group':
            await bot.send(event, str(Groups))
        await bot.send(event, f'命令 {payload} 执行成功。')

    bot.run()

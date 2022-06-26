# 为机器人的所有好友和群发送通知（如下线通知
# 极其不建议使用！！！会被封号
import asyncio
import pprint

from mirai import Mirai, WebSocketAdapter, FriendMessage
from mirai import Startup, Shutdown, MessageEvent
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain, MessageChain, Image

if __name__ == '__main__':
    bot = Mirai(
        qq=3409201437,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='yirimirai', host='localhost', port=8080
        )
    )

    # @bot.on(MessageEvent)
    # async def send_notice(event: MessageEvent):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     if msg.strip() == '.test':
    #         group_list = await bot.group_list.get()
    #         pprint.pprint(group_list)

    @bot.on(Startup)
    async def send_notice():
        group_list = list(await bot.group_list.get())
        for group in group_list:
            try:
                print(group)
                await asyncio.sleep(0.5)
                await bot.send_group_message(group.id, "机器人暂时下线哦~，正在进行功能测试（群发消息）")
            except:
                print("不存在群号为 {} 的群组".format(group))

        friend_list = list(await bot.friend_list.get())
        for friend in friend_list:
            try:
                print(friend)
                await asyncio.sleep(0.5)
                await bot.send_friend_message(friend.id, "机器人暂时下线哦~，正在进行功能测试（群发消息）")
            except:
                print("不存在qq号为 {} 的好友".format(friend))
        exit(0)


    bot.run()

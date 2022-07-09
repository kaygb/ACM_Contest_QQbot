感谢大佬：
* 特别感谢[guke1024](https://github.com/guke1024)帮我一起完善这个项目qwq
* [CodeCat](https://github.com/CodeCat-maker)帮我一起完善这个项目qwq
* [neal](https://github.com/neal2018)帮我一起完善这个项目qwq
* [SirlyDreamer](https://github.com/SirlyDreamer)帮我一起完善这个项目qwq

## 公告
可以看一下guke1024根据本项目进行扩充的项目：https://github.com/guke1024/ACM_QQbot

~~直接clone项目可能会很难克隆，因为我在第一版上传的时候把mirai放入git然后传进github上了，如果想二次开发或者fork后，最好直接选择下载源码zip来下载（才不是我没研究明白删记录不想删）~~

由于本项目使用了LFS，只能通过git lfs clone的方式下载仓库，否则图片会出问题qwq ~~已经在push作者删除之前的mirai记录了~~

### 项目介绍
本项目是一个在群里可以通知打cf的机器人项目，以及通知或者查询其他比赛的通知机器人，如果您觉得项目写的不错可以点一下右上角的✨`Star`，谢谢啦


### 功能介绍
目前实现的功能有：
* 查询CF比赛
* 查询对应id的cf分数
* 随机CF round网址（随机近180天到3年内的vp）
* 随机固定场次类型
* 查询AtCoder比赛
* 查询AtCoder对应id的rating分数
* 查询力扣的比赛
* 查询牛客比赛
* 查询当日所有比赛信息
* 通知当日所有比赛信息，并可自助添加想要通知的对象（删除还没想好，可能得用数据库）
* 查询下一场比赛信息
* 来只清楚->随机发送清楚姐姐图片
* 添加清楚->使用qq回复功能选择图片回复发送“添加清楚”
* 来只yxc->随机发送yxc图片
* 来只叉姐->随机发送叉姐锐评
* CF上下号提醒
* 市级城市的天气查询
* Log功能
* 查询牛客rating（目前功能不完善，不建议使用）
* ....

还在计划中的功能：
* 补充代码注释
* 通过CF的round号来找到对应网址
* 洛谷相关功能
  * （还没想好)
* 比赛倒计时功能
* ...

目前已知bug：
* 暂无，上版本bug全已修复

### 接口调用
本项目基于Python3.8.10为主要开发版本，以[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 为主要依赖库

### 部署方法

1. 环境配置
   * 请参照YiriMirai的教程环境配置：https://yiri-mirai.wybxc.cc/tutorials/01/configuration
   * 建议更新Mirai到最新版本，使用命令`./mcl -u`

2. 使用Mirai登陆qq https://yiri-mirai.wybxc.cc/tutorials/01/configuration#4-%E7%99%BB%E5%BD%95-qq

3. 挂起服务（如果是linux服务器，参照官网教程，如何挂起而不退出：https://yiri-mirai.wybxc.cc/tutorials/02/linux）

4. clone到本地或者服务器中（不要直接下载源码，如果网速慢请挂梯子）

注意：本仓库使用了LFS，可能需要额外安装 `git-lfs`，否则图片clone下来并不是图片，随机清楚等功能会产生异常
~~~shell
sudo apt install git-lfs
git clone https://github.com/INGg/ACM_Contest_QQbot.git
~~~

5. 修改`main.py`中bot的qq号为你自己的qq号
~~~python
bot = Mirai(
    qq=*****,  # 改成你的机器人的 QQ 号
    adapter=WebSocketAdapter(
        verify_key='yirimirai', host='localhost', port=8080
    )
)
hdc = HandlerControl(bot)  # 事件接收器
~~~

6. 安装对应的库
~~~shell
pip3 install -r ./requirements.txt
# 应该是全了qwq，如果不全请根据报错来安装相应的包，如果方便请您告知我，我将更新安装命令
~~~

7. 启动bot
~~~shell
python3 main.py
# 或 python main.py
# 自己编译安装python3.8的 python3.8 main.py
~~~
